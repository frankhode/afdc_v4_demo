import json, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class ImageImport(unittest.TestCase):
 def test_only_selected_images_and_no_metadata(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);data=root/'docs/data';data.mkdir(parents=True)
   cat=data/'catalog.json';cat.write_text(json.dumps({'meta':{'imagesIncluded':0},'records':[{'images':[{'id':'FO000001_001','src':None,'thumb':None}]}]}))
   im=Image.new('RGB',(2200,1000),'white');exif=Image.Exif();exif[270]='Private source description';im.save(root/'source.jpg',exif=exif)
   with zipfile.ZipFile(root/'input.zip','w') as z:
    z.write(root/'source.jpg','../private/FO000001_001.jpg');z.write(root/'source.jpg','FO999999_001.jpg')
   proc=subprocess.run([sys.executable,str(ROOT/'scripts/import_images.py'),str(root/'input.zip'),'--catalog',str(cat),'--confirmed-public'],capture_output=True,text=True)
   self.assertEqual(proc.returncode,0,proc.stderr)
   result=json.loads(cat.read_text());self.assertEqual(result['meta']['imagesIncluded'],1)
   out=root/'docs/assets/images/FO000001_001.webp'
   with Image.open(out) as image:
    self.assertLessEqual(max(image.size),1600);self.assertEqual(len(image.getexif()),0)
   self.assertFalse((root/'private').exists());self.assertFalse((out.parent/'FO999999_001.webp').exists())
if __name__=='__main__':unittest.main()
