#!/usr/bin/env python3
"""Fail closed on data fields, broken references, internal paths and non-static files."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DOCS=ROOT/'docs'
d=json.loads((DOCS/'data/catalog.json').read_text(encoding='utf-8'))
assert set(d)=={'meta','records','collections'}
assert set(d['meta'])=={'sourceRepository','sourceCommit','snapshotDate','schemaVersion','imagesIncluded'}
ids=set();images=set();total=0
for r in d['records']:
 assert set(r)=={'id','sys','title','originalNumber','date','subjects','digitalCount','images'},r.keys()
 assert re.fullmatch(r'FO\d{6}',r['id']) and r['id'] not in ids;ids.add(r['id'])
 for s in r['subjects']:
  assert set(s)=={'field','term'} and s['field'] in {'600','610','611','630','650','651','655'}
 for im in r['images']:
  assert set(im)=={'id','src','thumb'} and im['id'].startswith(r['id']+'_')
  assert re.fullmatch(r'FO\d{6}_\d+',im['id']) and im['id'] not in images;images.add(im['id'])
  for k in ('src','thumb'):
   if im[k]: assert re.fullmatch(r'assets/images/[A-Za-z0-9_.-]+',im[k]) and (DOCS/im[k]).is_file()
  assert bool(im['src'])==bool(im['thumb'])
  total+=bool(im['src'])
for c in d['collections']:
 assert set(c)=={'id','title','description','origin','recordIds','imageIds'}
 assert set(c['recordIds'])<=ids and set(c['imageIds'])<=images
assert total==d['meta']['imagesIncluded']
for p in DOCS.rglob('*'):
 if not p.is_file(): continue
 assert p.suffix.lower() not in {'.sql','.php','.sqlite','.db','.zip','.bak'},p
 if p.suffix in {'.json','.html','.mjs','.css'}:
  s=p.read_text(encoding='utf-8')
  assert not re.search(r'password_hash|owner_user_id|created_by_user_id|[A-Z]:\\\\|(?:localhost|127\.0\.0\.1):3306',s),p
print(f'OK: {len(ids)} sobres; {len(images)} referencias; {len(d["collections"])} colecciones; {total} imágenes disponibles.')
