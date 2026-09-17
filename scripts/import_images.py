#!/usr/bin/env python3
"""Import selected JPEG/PNG/TIFF images; resize and strip metadata. No ZIP extraction."""
import argparse, io, json, re, zipfile
from pathlib import Path
from PIL import Image, ImageOps

def key(name):
    m=re.search(r'(FO\d{6}_\d+)',Path(name).stem,re.I)
    return m[1].upper() if m else None

def inputs(source):
    if source.is_dir():
        for p in sorted(source.rglob('*')):
            if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png','.tif','.tiff','.webp'}:
                yield str(p),lambda p=p:p.read_bytes()
    else:
        with zipfile.ZipFile(source) as z:
            for i in sorted(z.infolist(),key=lambda x:x.filename):
                if i.is_dir() or Path(i.filename).suffix.lower() not in {'.jpg','.jpeg','.png','.tif','.tiff','.webp'}: continue
                if i.file_size>80_000_000: raise ValueError('Image too large: '+Path(i.filename).name)
                yield i.filename,lambda i=i:z.read(i)

def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--catalog',type=Path,default=Path('docs/data/catalog.json'));p.add_argument('--confirmed-public',action='store_true',help='The supplied images have been cleared for public demo use.');a=p.parse_args()
    if not a.confirmed_public:p.error('Use --confirmed-public only with images cleared for the public demo.')
    d=json.loads(a.catalog.read_text(encoding='utf-8'));selected={i['id']:i for r in d['records'] for i in r['images']};out=a.catalog.parent.parent/'assets/images';out.mkdir(parents=True,exist_ok=True)
    seen=set();count=0;ignored=0
    for name,read in inputs(a.source):
        k=key(name)
        if k not in selected: ignored+=1;continue
        if k in seen: raise ValueError('Duplicate image ID in input: '+k)
        seen.add(k)
        with Image.open(io.BytesIO(read())) as original:
            im=ImageOps.exif_transpose(original).convert('RGB');im.thumbnail((1600,1600))
            # New pixel-only object drops EXIF, GPS, comments, ICC and other source metadata.
            clean=Image.new('RGB',im.size);clean.paste(im)
            clean.save(out/(k+'.jpg'),quality=84,optimize=True)
            clean.thumbnail((320,320));clean.save(out/(k+'.thumb.jpg'),quality=78,optimize=True)
        selected[k]['src']='assets/images/'+k+'.jpg';selected[k]['thumb']='assets/images/'+k+'.thumb.jpg';count+=1
    d['meta']['imagesIncluded']=sum(bool(i['src']) for i in selected.values());a.catalog.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'imported':count,'notSelected':ignored,'totalAvailable':d['meta']['imagesIncluded'],'pending':sum(not i['src'] for i in selected.values())}))
if __name__=='__main__':main()
