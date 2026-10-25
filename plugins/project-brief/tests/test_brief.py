import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
spec=importlib.util.spec_from_file_location('brief',Path(__file__).with_name('brief.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class Tests(unittest.TestCase):
 def setUp(self):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
  for name,text in [('idea.md','Community garden proposal. Not implemented.'),('arabic.md','مقترح حديقة لم ينفذ بعد.'),('evidence.txt','Interview')]: (self.root/name).write_text(text)
  self.d={'version':1,'primary_language':'en','topics':{'purpose':{'visibility':'public','variants':{l:{'path':p,'direction':dr} for l,p,dr in [('en','idea.md','ltr'),('ar','arabic.md','rtl')]},'evidence':[{'ref':'evidence.txt'}],'claims':{'stage':'proposal'}}},'recipes':{'pitch':{'topics':['purpose'],'visibility':'public','perspective':'Organizer','priorities':['Accessibility'],'max_chars':1000}}}
  self.stamp()
 def stamp(self):
  for t in self.d['topics'].values():
   for l,v in t['variants'].items():v['review']={**b.fingerprints(self.root,self.d,t,l),'at':'2026-10-25'}
 def test_nonsoftware_no_git(self):
  self.assertFalse((self.root/'.git').exists());self.assertFalse(any(x['needs_review'] for x in b.check(self.root,self.d)))
  self.assertIn('garden',b.markdown(b.export(self.root,self.d,'pitch','en')))
 def test_arabic_missing_translation(self):
  self.assertEqual(b.export(self.root,self.d,'pitch','ar')['topics'][0]['direction'],'rtl')
  with self.assertRaises(b.BriefError):b.export(self.root,self.d,'pitch','fr')
 def test_primary_change_stales_translation(self):
  (self.root/'idea.md').write_text('New proposal')
  self.assertIn('primary-changed',b.check(self.root,self.d)[1]['needs_review'])
  with self.assertRaises(b.BriefError):b.export(self.root,self.d,'pitch','ar')
 def test_evidence_and_claims(self):
  (self.root/'evidence.txt').write_text('New findings');self.d['topics']['purpose']['claims']['stage']='implemented'
  issues=b.check(self.root,self.d)[0]['needs_review']
  self.assertIn('evidence-changed',issues);self.assertIn('claims-changed',issues)
 def test_unrelated_edit(self):
  (self.root/'other.rs').write_text('fn main() {}')
  self.assertFalse(any(x['needs_review'] for x in b.check(self.root,self.d)))
 def test_public_internal_isolation(self):
  self.d['topics']['purpose']['visibility']='internal'
  with self.assertRaises(b.BriefError):b.export(self.root,self.d,'pitch','en')
 def test_stale_override_internal_only(self):
  (self.root/'idea.md').write_text('Unreviewed')
  with self.assertRaises(b.BriefError):b.export(self.root,self.d,'pitch','en',True)
  self.d['recipes']['pitch']['visibility']='internal'
  self.assertTrue(b.export(self.root,self.d,'pitch','en',True)['topics'][0]['needs_review'])
 def test_public_metadata(self):
  self.assertNotIn('evidence.txt',json.dumps(b.export(self.root,self.d,'pitch','en')))
 def test_no_silent_truncation(self):
  self.d['recipes']['pitch']['max_chars']=5
  with self.assertRaises(b.BriefError):b.export(self.root,self.d,'pitch','en')
 def test_path_symlink_escape(self):
  with self.assertRaises(b.BriefError):b.read(self.root,'../outside')
  (self.root/'escape').symlink_to('/etc/hosts')
  with self.assertRaises(b.BriefError):b.read(self.root,'escape')
 def test_block_boundaries(self):
  p=self.root/'idea.md';p.write_text('other\n<!-- project-brief:start id=x lang=en -->\nSelected\n<!-- project-brief:end id=x lang=en -->')
  t=self.d['topics']['purpose'];t['variants']['en']['block']='x'
  self.assertEqual(b.content(self.root,t,'en'),'Selected');p.write_text(p.read_text()*2)
  with self.assertRaises(b.BriefError):b.content(self.root,t,'en')
 def test_version_validation(self):
  p=self.root/'project-brief.json';p.write_text(json.dumps(self.d));b.load(self.root,p.name)
  self.d['version']=2;p.write_text(json.dumps(self.d))
  with self.assertRaises(b.BriefError):b.load(self.root,p.name)
 def test_other_stack_perspective_delivery(self):
  (self.root/'main.go').write_text('package main');self.d['topics']['purpose']['evidence']=[{'ref':'main.go'}]
  self.d['recipes']['pitch'].update(perspective='Independent evaluator',delivery='Audio script',priorities=['Maintainability']);self.stamp()
  self.assertEqual(b.export(self.root,self.d,'pitch','en')['brief']['delivery'],'Audio script')
 def test_cli_review_requires_explicit_acknowledgement(self):
  config=self.root/'project-brief.json'
  del self.d['topics']['purpose']['variants']['en']['review']
  config.write_text(json.dumps(self.d))
  command=[sys.executable,str(Path(b.__file__).resolve()),'review','--root',str(self.root),'--topic','purpose','--language','en']
  before=config.read_text()
  denied=subprocess.run(command,capture_output=True,text=True)
  self.assertEqual(denied.returncode,2);self.assertEqual(config.read_text(),before)
  accepted=subprocess.run(command+['--acknowledge-reviewed'],capture_output=True,text=True)
  self.assertEqual(accepted.returncode,0,accepted.stderr)
  stored=json.loads(config.read_text())
  self.assertIn('review',stored['topics']['purpose']['variants']['en'])
  self.assertEqual(stored['topics']['purpose']['variants']['ar'],self.d['topics']['purpose']['variants']['ar'])
 def test_stale_markdown_has_visible_warning(self):
  self.d['recipes']['pitch']['visibility']='internal'
  (self.root/'idea.md').write_text('Changed')
  text=b.markdown(b.export(self.root,self.d,'pitch','en',True))
  self.assertIn('REVIEW REQUIRED',text)
if __name__=='__main__':unittest.main()
