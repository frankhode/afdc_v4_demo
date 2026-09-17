#!/usr/bin/env python3
"""Read phpMyAdmin INSERTs without executing SQL; export an explicit field allowlist."""
import argparse, collections, hashlib, json, re
from pathlib import Path

TABLES={'titulos','materias','digitales','collections_v2','collection_items_v2'}
def values(text):
    i=0
    while i<len(text):
        if text[i]!='(': i+=1; continue
        i+=1; row=[]
        while True:
            while text[i].isspace(): i+=1
            if text[i]=="'":
                i+=1; out=[]
                while True:
                    c=text[i]; i+=1
                    if c=='\\':
                        c=text[i]; i+=1; out.append({'n':'\n','r':'\r','t':'\t','0':'\0','Z':'\x1a'}.get(c,c))
                    elif c=="'":
                        if i<len(text) and text[i]=="'": out.append("'"); i+=1
                        else: break
                    else: out.append(c)
                row.append(''.join(out))
            else:
                start=i
                while text[i] not in ',)': i+=1
                v=text[start:i].strip(); row.append(None if v=='NULL' else v)
            while text[i].isspace(): i+=1
            c=text[i]; i+=1
            if c==')': break
            if c!=',': raise ValueError('Malformed SQL tuple')
        yield row

def read_tables(path):
    tables=collections.defaultdict(list); table=None; columns=[]; buf=[]
    with path.open(encoding='utf-8-sig') as f:
        for line in f:
            if table is None:
                m=re.match(r'INSERT INTO `([^`]+)` \((.*?)\) VALUES\s*(.*)',line)
                if not m or m[1] not in TABLES: continue
                table=m[1]; columns=re.findall(r'`([^`]+)`',m[2]); buf=[m[3]]
            else: buf.append(line)
            if line.rstrip().endswith(';'):
                for row in values(''.join(buf)):
                    if len(row)!=len(columns): raise ValueError(f'Column mismatch: {table}')
                    tables[table].append(dict(zip(columns,row)))
                table=None; buf=[]
    if table: raise ValueError('Truncated SQL')
    return tables

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def image_key(name):
    m=re.search(r'(FO\d{6}_\d+)',name or '',re.I)
    return m[1].upper() if m else None

def main():
    p=argparse.ArgumentParser(); p.add_argument('sql',type=Path); p.add_argument('--output',type=Path,default=Path('docs/data/catalog.json')); a=p.parse_args()
    t=read_tables(a.sql)
    subjects=collections.defaultdict(list)
    for r in t['materias']:
        if r['campo'] in ['600','610','611','630','650','651','655'] and clean(r['materia']):
            s={'field':r['campo'],'term':clean(r['materia'])}
            if s not in subjects[r['sys']]: subjects[r['sys']].append(s)
    digital=collections.defaultdict(dict)
    for r in t['digitales']:
        k=image_key(r['nombramiento'])
        if r['carpeta']=='Bajas' and k: digital[r['inv']][k]=r['nombramiento']
    titles={}
    for r in t['titulos']:
        if re.fullmatch(r'FO\d{6}',r['barcode'] or '') and clean(r['titulo']): titles.setdefault(r['barcode'],r)
    public={r['id']:r for r in t['collections_v2'] if r['is_public']=='1'}
    public_items=[r for r in t['collection_items_v2'] if r['collection_id'] in public and r['item_type']=='foto' and image_key(r['image_key'])]
    chosen={image_key(r['image_key']).split('_')[0] for r in public_items} & titles.keys()
    # Sport/culture selection; exclude potentially sensitive crime/health subject matter.
    excluded=re.compile(r'asesinat|cadáver|cadaver|violaci|detenid|desnud|hospital|accidente|suicid|secuestro|menor de|represi|tortur|muert|operad|enferm|bombarde|montonero|policía|juez|casamiento|casó|familia|flia|vedet|gorda|prohib',re.I)
    groups=[('futbol','Fútbol argentino',r'fútbol|futbol|futbolista',36),('musica','Música y escenarios',r'música|musica|cantante|músico|musico|recital|concierto',24),('ciudad','Teatro, arte y ciudad',r'teatro|teatral|arquitectura|exposici|museo',24)]
    group_ids={}; candidates=sorted(titles.values(),key=lambda r:hashlib.sha256(r['barcode'].encode()).hexdigest())
    for gid,label,pattern,limit in groups:
        selected=[]
        for r in candidates:
            text=r['titulo']+' '+ ' '.join(s['term'] for s in subjects[r['sys']])
            if digital[r['barcode']] and re.search(pattern,text,re.I) and not excluded.search(text):
                selected.append(r['barcode'])
                if len(selected)==limit: break
        chosen.update(selected); group_ids[gid]=selected
    records=[]
    for barcode in sorted(chosen):
        r=titles[barcode]
        # Prioritize exact public-collection frames, then up to four per envelope.
        keys=sorted(digital[barcode]); wanted=[image_key(x['image_key']) for x in public_items if image_key(x['image_key']).startswith(barcode+'_')]
        keys=list(dict.fromkeys([k for k in wanted if k in keys]+keys[:4]))
        records.append({'id':barcode,'sys':clean(r['sys']),'title':clean(r['titulo']),'originalNumber':clean(r['nroA']),'date':clean(r['fecha']),'subjects':subjects[r['sys']],'digitalCount':len(digital[barcode]),'images':[{'id':k,'src':None,'thumb':None} for k in keys]})
    image_ids={im['id'] for r in records for im in r['images']}
    collections_out=[]
    for cid,c in public.items():
        images=[image_key(i['image_key']) for i in sorted(public_items,key=lambda x:int(x['position'] or 0)) if i['collection_id']==cid and image_key(i['image_key']) in image_ids]
        if images: collections_out.append({'id':'public-'+cid,'title':clean(c['title']),'description':'Selección pública conservada de la base original.','origin':'public','imageIds':list(dict.fromkeys(images)),'recordIds':list(dict.fromkeys(x.split('_')[0] for x in images))})
    for gid,label,_,_ in groups:
        collections_out.append({'id':gid,'title':label,'description':'Recorrido temático creado para esta demo con registros reales.','origin':'demo','recordIds':group_ids[gid],'imageIds':[]})
    out={'meta':{'sourceRepository':'frankhode/afdc_v4','sourceCommit':'2ae40e23c5dbeab82451a6228a99055783572b40','snapshotDate':'2026-07-31','schemaVersion':1,'imagesIncluded':0},'records':records,'collections':collections_out}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    manifest=[{'imageId':im['id'],'recordId':r['id'],'sourceFilename':digital[r['id']][im['id']]} for r in records for im in r['images']]
    (a.output.parent/'images-requested.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'records':len(records),'imagesRequested':len(manifest),'collections':len(collections_out),'tablesRead':{k:len(v) for k,v in t.items()}},ensure_ascii=False))
if __name__=='__main__': main()
