#!/usr/bin/env python3
"""فحص تغليف محافظ بلا شبكة، Python 3.8+؛ ليس محلل YAML عامًا."""
import argparse
import json
import re
from pathlib import Path

SKILLS = {'ksaa-context', 'ksaa-govern', 'ksaa-harness', 'ksaa-spec', 'ksaa-plan',
          'ksaa-architecture', 'ksaa-build', 'ksaa-test', 'ksaa-game-qa',
          'ksaa-language-qa', 'ksaa-security', 'ksaa-ci', 'ksaa-docs', 'ksaa-review',
          'ksaa-release', 'ksaa-measure'}
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
VERSION = re.compile(r'^\d+\.\d+\.\d+$')
LINK = re.compile(r'\[[^\]\n]+\]\(([^)\n]+)\)')
# إشارات عامة فقط؛ لا تغني عن مراجعة خصوصية بشرية أو ماسح أسرار معتمد.
PUBLIC_BLOCKS = [
    re.compile(r'https?://github\.com/ksaa-nlp/(?!marketplace(?:[/#?\s)]|$))[^\s)]+', re.I),
    re.compile(r'(?:/workspace/|/Users/|/home/|/root/)[^\s`]+'),
    re.compile(r'https?://[^\s/]+\.(?:internal|local|corp)(?:[/:\s]|$)', re.I),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'\b(?:ghp_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16})\b'),
]


def within(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def frontmatter(text, expected_name):
    """يدعم فقط name كـslug وdescription كسلسلة JSON مقتبسة صالحة في YAML."""
    errors = []
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        return ['missing frontmatter']
    try:
        end = lines.index('---', 1)
    except ValueError:
        return ['unclosed frontmatter']
    fields = {}
    for line in lines[1:end]:
        if ': ' not in line:
            errors.append('unsupported frontmatter syntax')
            continue
        key, value = line.split(': ', 1)
        if key in fields:
            errors.append('duplicate frontmatter field')
        fields[key] = value
    if set(fields) != {'name', 'description'}:
        errors.append('frontmatter fields must be name and description')
    name = fields.get('name', '')
    if name != expected_name or not SLUG.fullmatch(name) or len(name) > 64:
        errors.append('invalid skill name')
    try:
        description = json.loads(fields.get('description', ''))
        if not isinstance(description, str) or not description.strip():
            raise ValueError('description must be string')
        if not re.search(r'[\u0600-\u06ff]', description):
            errors.append('description must be Arabic')
    except (ValueError, TypeError):
        errors.append('description must be a JSON-quoted string (YAML-safe subset)')
    if not '\n'.join(lines[end + 1:]).strip():
        errors.append('empty skill body')
    return errors


def read_json(path, errors):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('object required')
        return data
    except (OSError, ValueError) as exc:
        errors.append('%s: invalid JSON (%s)' % (path.name, exc))
        return {}


def check_baseline(root, baseline):
    errors = []
    mutable = {'README.md', '.claude-plugin/marketplace.json'}
    for old in baseline.rglob('*'):
        if not old.is_file() or any(part in {'.git', '__pycache__'} for part in old.relative_to(baseline).parts) or old.suffix == '.pyc':
            continue
        rel = old.relative_to(baseline).as_posix()
        new = root / rel
        if not new.is_file():
            errors.append('baseline file missing: ' + rel)
        elif rel not in mutable and old.read_bytes() != new.read_bytes():
            errors.append('baseline file changed: ' + rel)
    old_readme = baseline / 'README.md'
    new_readme = root / 'README.md'
    if old_readme.is_file() and new_readme.is_file():
        iterator = iter(new_readme.read_text(encoding='utf-8').splitlines())
        for line in old_readme.read_text(encoding='utf-8').splitlines():
            if not any(candidate == line for candidate in iterator):
                errors.append('baseline README lines were removed/reordered')
                break
    old = read_json(baseline / '.claude-plugin/marketplace.json', errors)
    new = read_json(root / '.claude-plugin/marketplace.json', errors)
    for key, value in old.items():
        if key not in {'plugins', 'metadata'} and new.get(key) != value:
            errors.append('baseline marketplace field changed: ' + key)
    for key, value in old.get('metadata', {}).items():
        if key != 'version' and new.get('metadata', {}).get(key) != value:
            errors.append('baseline marketplace metadata changed: ' + key)
    for entry in old.get('plugins', []):
        if entry not in new.get('plugins', []):
            errors.append('baseline plugin entry removed or changed')
    try:
        before = old['metadata']['version']
        after = new['metadata']['version']
        if not VERSION.fullmatch(after) or tuple(map(int, after.split('.'))) <= tuple(map(int, before.split('.'))):
            errors.append('marketplace version must increase')
    except (KeyError, TypeError, ValueError):
        errors.append('invalid marketplace version')
    return errors


def validate(root, baseline=None):
    errors = []
    root = Path(root).resolve()
    plugin = root / 'plugins' / 'ksaa-ai-dev'
    manifest = read_json(plugin / '.claude-plugin/plugin.json', errors)
    market = read_json(root / '.claude-plugin/marketplace.json', errors)
    if manifest.get('name') != 'ksaa-ai-dev':
        errors.append('invalid plugin name')
    version = manifest.get('version', '')
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        errors.append('invalid plugin version')
    if not isinstance(manifest.get('description'), str) or not re.search(r'[\u0600-\u06ff]', manifest.get('description', '')):
        errors.append('plugin description must be Arabic')
    entries = market.get('plugins', [])
    if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
        errors.append('invalid marketplace plugins list')
        entries = []
    names = [e.get('name') for e in entries]
    if len(names) != len(set(str(n) for n in names)):
        errors.append('duplicate marketplace plugin name')
    for entry in entries:
        name = entry.get('name', '')
        if not isinstance(name, str) or not SLUG.fullmatch(name):
            errors.append('invalid marketplace plugin name')
    matches = [e for e in entries if e.get('name') == 'ksaa-ai-dev']
    if len(matches) != 1 or matches[0].get('source') != './plugins/ksaa-ai-dev':
        errors.append('missing/invalid marketplace registration')
    elif matches[0].get('version') != version:
        errors.append('marketplace/plugin version mismatch')
    skill_files = list((plugin / 'skills').glob('*/SKILL.md'))
    found = {f.parent.name for f in skill_files}
    if found != SKILLS:
        errors.append('skill inventory mismatch: missing=%s extra=%s' % (sorted(SKILLS-found), sorted(found-SKILLS)))
    for skill in skill_files:
        if not within(skill, plugin):
            errors.append('skill escapes plugin')
            continue
        errors.extend('%s: %s' % (skill.parent.name, e) for e in frontmatter(skill.read_text(encoding='utf-8'), skill.parent.name))
    linked = set()
    markdown = list(plugin.rglob('*.md'))
    for path in plugin.rglob('*'):
        if path.is_symlink():
            errors.append('symlink not allowed in published plugin: ' + str(path.relative_to(plugin)))
        if path.is_file() and not within(path, plugin):
            errors.append('file escapes plugin')
    for md in markdown:
        if not within(md, plugin):
            continue
        content = md.read_text(encoding='utf-8')
        for pattern in PUBLIC_BLOCKS:
            if pattern.search(content):
                errors.append('public-safety signal: ' + str(md.relative_to(plugin)))
        for raw in LINK.findall(content):
            if raw.startswith(('https://', 'http://', 'mailto:', '#')):
                continue
            target = raw.split('#', 1)[0]
            if not target:
                continue
            resolved = (md.parent / target).resolve()
            if not within(resolved, plugin):
                errors.append('reference escapes plugin: %s -> %s' % (md.relative_to(plugin), target))
            elif not resolved.exists():
                errors.append('broken local link: %s -> %s' % (md.relative_to(plugin), target))
            else:
                linked.add(resolved)
    for folder in ['references', 'templates']:
        for path in (plugin / folder).rglob('*'):
            if path.is_file() and path.resolve() not in linked:
                errors.append('undiscoverable resource: ' + str(path.relative_to(plugin)))
    for needed in ['README.md', 'scripts/check-gate-evidence.py', 'tests/test-validation.py', 'tests/test-gate-evidence.py']:
        if not (plugin / needed).is_file():
            errors.append('required packaging resource missing: ' + needed)
    if baseline:
        errors.extend(check_baseline(root, Path(baseline).resolve()))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--marketplace', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    errors = validate(args.marketplace, args.baseline)
    for error in errors:
        print('ERROR:', error)
    if not errors:
        print('OK: packaging, strict frontmatter subset, local links and public-safety signals' + ('; baseline preserved' if args.baseline else ''))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
