import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from extract_sample import values, read_tables
class Extraction(unittest.TestCase):
 def test_values(self):
  self.assertEqual(list(values("('O\\'Brien', 'a,b (c); d', NULL, 'a\\nb', 'Peña', 'it''s'),('x', 'y', 12, '', '', '');")), [["O'Brien",'a,b (c); d',None,'a\nb','Peña',"it's"],['x','y','12','','','']])
 def test_allowlist(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'input.sql'
   p.write_text("INSERT INTO `users` (`id`, `password_hash`) VALUES\n(1, 'secret');\nINSERT INTO `titulos` (`sys`, `titulo`) VALUES\n('001', 'Título \\'prueba\\'');\n",encoding='utf-8')
   result=read_tables(p);self.assertNotIn('users',result);self.assertEqual(result['titulos'][0]['titulo'],"Título 'prueba'")
if __name__=='__main__':unittest.main()
