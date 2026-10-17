"""Offline delivery gate: files, local HTML dependencies, plan and planned tests."""
from pathlib import Path
from html.parser import HTMLParser
import json,sys,re
from urllib.parse import unquote
def check(root):
 root=Path(root).resolve();errors=[]
 class Parser(HTMLParser):
  def handle_starttag(self,tag,attrs):
   a=dict(attrs)
   if tag=='script' and a.get('src'):refs.append(a['src'])
   if tag=='link' and a.get('rel')=='stylesheet' and a.get('href'):refs.append(a['href'])
 if not (root/'index.html').is_file():return ['missing index.html']
 if not (root/'.nojekyll').is_file():errors.append('missing .nojekyll for static GitHub Pages delivery')
 refs=[];Parser().feed((root/'index.html').read_text(encoding='utf-8-sig'))
 for ref in refs:
  if ref.startswith(('http:','https:','//')):errors.append('offline dependency is remote: '+ref);continue
  if ref.startswith('data:'):continue
  webpath=unquote(ref.split('?')[0].split('#')[0])
  if webpath.startswith(('/', '\\')) or re.match(r'^[A-Za-z]:',webpath):errors.append('nonportable absolute dependency: '+ref);continue
  p=root/webpath
  if not p.resolve().is_relative_to(root):errors.append('dependency escapes demo directory: '+ref);continue
  current=root
  for part in Path(webpath).parts:
   if part=='.':continue
   if part=='..':current=current.parent;continue
   if current.is_dir() and part not in [x.name for x in current.iterdir()]:
    if any(x.name.lower()==part.lower() for x in current.iterdir()):errors.append('dependency filename case mismatch: '+ref)
   current=current/part
  if not p.is_file() or not p.stat().st_size:errors.append('missing/empty dependency: '+ref)
 try:plan=json.loads((root/'delivery-plan.json').read_text(encoding='utf-8-sig'))
 except (OSError,ValueError) as e:return errors+['missing/invalid delivery-plan.json: '+str(e)]
 pages=plan.get('pages',[]);features=plan.get('features',[])
 if not pages or not features:errors.append('plan must contain pages and features')
 ids=[p.get('id') for p in pages]
 if len(set(ids))!=len(ids):errors.append('duplicate page id')
 for p in pages:
  if not p.get('id') or not p.get('contentSelector'):errors.append('page missing id/contentSelector')
  if not any(f.get('pageId')==p.get('id') for f in features):errors.append('page without tested functionality: '+str(p.get('id')))
 seen=set()
 for f in features:
  if not f.get('id') or f.get('id') in seen:errors.append('missing/duplicate feature id')
  seen.add(f.get('id'))
  if f.get('pageId') not in ids:errors.append('unknown page: '+str(f.get('pageId')))
  if not f.get('description') or not f.get('implementation'):errors.append('feature needs description and implementation: '+str(f.get('id')))
  for file in f.get('implementation',[]):
   p=root/file
   if not p.is_file() or not p.stat().st_size:errors.append('missing implementation: '+file)
  steps=f.get('steps',[])
  if not steps or not any(s.get('action') in ['expectText','expectCount','expectValue'] for s in steps):errors.append('feature missing observable assertion: '+str(f.get('id')))
 return errors
if __name__=='__main__':
 errors=check(sys.argv[1]);print(json.dumps({'passed':not errors,'scope':'static files and planned test coverage only','errors':errors},ensure_ascii=False,indent=2));sys.exit(bool(errors))
