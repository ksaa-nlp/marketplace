#!/usr/bin/env python3
"""Project Brief: optional, dependency-free tooling for portable briefing content."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

MAX_BYTES = 2_000_000

class BriefError(ValueError):
    pass

def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def local(root, name):
    if not isinstance(name, str) or not name:
        raise BriefError('A local path must be a nonempty string')
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise BriefError('Path escapes project root: ' + name)
    return path

def read(root, name):
    path = local(root, name)
    if path.stat().st_size > MAX_BYTES:
        raise BriefError('File exceeds 2 MB read limit: ' + name)
    return path.read_text(encoding='utf-8')

def load(root, config):
    data = json.loads(read(root, config))
    if data.get('version') != 1:
        raise BriefError('Unsupported manifest version; expected 1')
    for field in ('primary_language', 'topics', 'recipes'):
        if not data.get(field):
            raise BriefError('Missing manifest field: ' + field)
    if not isinstance(data['primary_language'], str):
        raise BriefError('primary_language must be a string')
    for collection in ('topics', 'recipes'):
        if not isinstance(data[collection], dict):
            raise BriefError(collection + ' must be an object')
        for key in data[collection]:
            if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', key):
                raise BriefError('Invalid stable ID: ' + key)
    for topic, entry in data['topics'].items():
        if not isinstance(entry, dict) or not isinstance(entry.get('variants'), dict):
            raise BriefError('Topic needs language variants: ' + topic)
        if data['primary_language'] not in entry['variants']:
            raise BriefError('Topic missing primary language: ' + topic)
        if entry.get('visibility') not in ('public', 'internal'):
            raise BriefError('Topic needs explicit public/internal visibility: ' + topic)
        if not isinstance(entry.get('evidence', []), list):
            raise BriefError('Evidence must be a list: ' + topic)
        for lang, variant in entry['variants'].items():
            if not re.fullmatch(r'[A-Za-z0-9-]+', lang) or not isinstance(variant, dict):
                raise BriefError('Invalid language variant: ' + topic)
            if not isinstance(variant.get('review', {}), dict):
                raise BriefError('Review must be an object: ' + topic)
            if variant.get('direction') not in ('rtl', 'ltr'):
                raise BriefError('Variant needs explicit rtl/ltr direction: ' + topic)
            if not isinstance(variant.get('path'), str):
                raise BriefError('Variant needs a path: ' + topic)
            if variant.get('block') is not None and not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', variant['block']):
                raise BriefError('Invalid block ID: ' + topic)
    for name, recipe in data['recipes'].items():
        ids = recipe.get('topics') if isinstance(recipe, dict) else None
        if not isinstance(ids, list) or not ids or len(set(ids)) != len(ids):
            raise BriefError('Recipe needs distinct, ordered topics: ' + name)
        if any(t not in data['topics'] for t in ids):
            raise BriefError('Unknown topic in recipe: ' + name)
        if recipe.get('visibility') not in ('public', 'internal'):
            raise BriefError('Recipe needs public/internal visibility: ' + name)
        limit = recipe.get('max_chars', 20000)
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200000:
            raise BriefError('Recipe max_chars must be 1–200000')
    return data

def content(root, topic, language):
    if language not in topic['variants']:
        raise BriefError('Requested translation is unavailable: ' + language)
    variant = topic['variants'][language]
    value = read(root, variant['path'])
    if variant.get('block'):
        block = variant['block']
        start = f'<!-- project-brief:start id={block} lang={language} -->'
        end = f'<!-- project-brief:end id={block} lang={language} -->'
        if value.count(start) != 1 or value.count(end) != 1 or value.index(start) >= value.index(end):
            raise BriefError('Missing, duplicated or reversed content markers: ' + block)
        value = value.split(start, 1)[1].split(end, 1)[0]
    if not value.strip():
        raise BriefError('Empty topic content')
    return value.strip()

def fingerprints(root, data, topic, language):
    # Only explicitly referenced files are read; no project scan or external calls.
    evidence = {}
    for item in topic.get('evidence', []):
        if not isinstance(item, dict) or not isinstance(item.get('ref'), str):
            raise BriefError('Evidence needs a ref')
        ref = item['ref']
        if ref.startswith(('https://', 'http://')):
            # URL is a reference, never proof of current external operation.
            evidence[ref] = item.get('reviewed_reference', 'unverified-external-reference')
        else:
            evidence[ref] = digest(read(root, ref))
    return {'content': digest(content(root, topic, language)),
            'primary': digest(content(root, topic, data['primary_language'])),
            'evidence': evidence,
            'claims': digest(json.dumps(topic.get('claims', {}), sort_keys=True, ensure_ascii=False))}

def status(root, data, topic, language):
    current = fingerprints(root, data, topic, language)
    reviewed = topic['variants'][language].get('review', {})
    issues = []
    if not reviewed.get('at'):
        issues.append('not-reviewed')
    for key in ('content', 'primary', 'evidence', 'claims'):
        if reviewed.get(key) != current[key]:
            issues.append(key + '-changed')
    return issues, current

def check(root, data):
    results = []
    for name, topic in data['topics'].items():
        for language in topic['variants']:
            issues, _ = status(root, data, topic, language)
            results.append({'topic': name, 'language': language, 'needs_review': issues})
    return results

def export(root, data, recipe_id, language, allow_stale=False):
    if recipe_id not in data['recipes']:
        raise BriefError('Unknown recipe: ' + recipe_id)
    recipe = data['recipes'][recipe_id]
    blocks = []
    for name in recipe['topics']:
        topic = data['topics'][name]
        if recipe['visibility'] == 'public' and topic['visibility'] != 'public':
            raise BriefError('Public recipe selects internal content: ' + name)
        issues, current = status(root, data, topic, language)
        if issues and (not allow_stale or recipe['visibility'] == 'public'):
            raise BriefError('Review required for ' + name + ': ' + ', '.join(issues))
        item = {'id': name, 'text': content(root, topic, language),
                'direction': topic['variants'][language]['direction'],
                'needs_review': issues, 'fingerprint': digest(json.dumps(current, sort_keys=True)),
                'reviewed_at': topic['variants'][language].get('review', {}).get('at')}
        if recipe['visibility'] == 'internal':
            item['claims'] = topic.get('claims', {})
            item['evidence'] = topic.get('evidence', [])
        blocks.append(item)
    # Refuse truncation: otherwise caveats or Arabic sentences could be silently lost.
    if sum(len(b['text']) for b in blocks) > recipe.get('max_chars', 20000):
        raise BriefError('Content exceeds recipe character budget; select fewer topics or edit a concise variant')
    result = {'version': 1, 'project': data.get('project', ''), 'language': language,
              'generated_at': datetime.now(timezone.utc).isoformat(),
              'recipe': recipe_id, 'brief': {k: recipe[k] for k in
              ('audience', 'perspective', 'priorities', 'delivery', 'purpose') if k in recipe},
              'topics': blocks}
    result['content_fingerprint'] = digest(json.dumps({'topics': blocks, 'brief': result['brief'], 'language': language, 'project': result['project']}, sort_keys=True, ensure_ascii=False))
    return result

def markdown(pack):
    # JSON holds the detailed provenance; Markdown remains human-readable.
    title = pack['project'] or 'Project Brief'
    header = f"# {title}\n\n{pack['language']} · {pack['recipe']}\n\n"
    header += f"<!-- Project Brief snapshot: {pack['generated_at']}; fingerprint={pack['content_fingerprint']} -->\n\n"
    return header + '\n\n'.join(('> REVIEW REQUIRED: ' + ', '.join(t['needs_review']) + '\n\n' if t['needs_review'] else '') + t['text'] for t in pack['topics']) + '\n'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'export', 'review'])
    parser.add_argument('--root', default='.')
    parser.add_argument('--config', default='project-brief.json')
    parser.add_argument('--recipe')
    parser.add_argument('--language')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown')
    parser.add_argument('--topic')
    parser.add_argument('--acknowledge-reviewed', action='store_true')
    parser.add_argument('--allow-stale', action='store_true')
    args = parser.parse_args()
    try:
        root = Path(args.root).resolve()
        data = load(root, args.config)
        if args.command == 'check':
            results = check(root, data)
            print(json.dumps(results, ensure_ascii=False, indent=2))
            return int(any(r['needs_review'] for r in results))
        language = args.language or data['primary_language']
        if args.command == 'review':
            if not args.acknowledge_reviewed or args.topic not in data['topics']:
                raise BriefError('Review requires --topic and --acknowledge-reviewed after checking content and evidence')
            topic = data['topics'][args.topic]
            _, fp = status(root, data, topic, language)
            topic['variants'][language]['review'] = {**fp, 'at': datetime.now(timezone.utc).isoformat()}
            path = local(root, args.config)
            staged = path.with_name(path.name + '.tmp')
            # Exclusive creation prevents following a pre-existing staging symlink.
            with staged.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
            staged.replace(path)
            print('Recorded editorial review; this is not independent verification.')
        else:
            result = export(root, data, args.recipe, language, args.allow_stale)
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.format == 'json' else markdown(result), end='\n')
        return 0
    except (BriefError, OSError, ValueError, KeyError, TypeError) as error:
        print('Project Brief: ' + str(error), file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
