import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {basic,advanced,search,terms,csv,hasImage} from '../docs/assets/search.mjs';
const data=JSON.parse(readFileSync(new URL('../docs/data/catalog.json',import.meta.url)));
const records=data.records;
test('real sample: basic search matches envelope metadata, not collection labels',()=>{
 const actual=records.filter(r=>basic(r,'maradona')).map(r=>r.id);
 assert.ok(actual.includes('FO077308'));
 // El Diego also includes match photographs; the envelope itself is not indexed by Maradona.
 assert.ok(!actual.includes('FO069829'));
 assert.ok(data.collections.find(c=>c.id==='public-1').recordIds.includes('FO069829'));
});
test('accent insensitive search',()=>{assert.ok(records.some(r=>basic(r,'musica')));assert.deepEqual(records.filter(r=>basic(r,'música')),records.filter(r=>basic(r,'MUSICA')));});
test('left to right boolean combination and NOT (different from SQL precedence)',()=>{
 const r={title:'uno',subjects:[],id:'FO000001',date:'19740101',originalNumber:''};
 const rows=[{field:'Titulo',term:'uno'},{op:'OR',field:'Titulo',term:'dos'},{op:'AND',field:'Titulo',term:'tres'}];
 assert.equal(advanced(r,rows),false);
 assert.equal(advanced(r,[{field:'Titulo',term:'dos',not:true}]),true);
 assert.equal(advanced(r,[{field:'Titulo',term:'   '},{field:'Titulo',term:'uno',op:'OR'}]),true);
});
test('refine applies across all hits and dates are inclusive',()=>{
 const result=search(records,{q:'Maradona',from:'1978',to:'1978',refine:'1978'});
 assert.ok(result.length>=2);for(const r of result)assert.equal(r.date.slice(0,4),'1978');
 assert.equal(search(records,{q:'not-existing-unique-query'}).length,0);
});
test('exact MARC match does not include partial or other-field terms',()=>{
 const r=records.find(r=>r.subjects.length);const s=r.subjects[0];
 const result=search(records,{field:s.field,term:s.term});assert.ok(result.includes(r));
 for(const hit of result)assert.ok(hit.subjects.some(x=>x.field===s.field&&x.term===s.term));
});
test('indices count envelopes once per term',()=>{
 for(const field of ['600','610','611','630','650','651','655'])for(const entry of terms(records,field))
  assert.equal(entry.count,search(records,{field,term:entry.term}).length);
});
test('available image filter never confuses SQL digital count with bundled files',()=>{
 assert.deepEqual(search(records,{images:true}),records.filter(hasImage));
 assert.equal(hasImage({images:[{src:null}],digitalCount:300}),false);
});
test('CSV escapes delimiters/quotes and neutralizes spreadsheet formulas',()=>{
 const r={sys:'1',id:'2',title:'=HYPERLINK("x")',date:'',subjects:[]};const text=csv([r]);
 assert.ok(text.startsWith('\uFEFF'));assert.ok(text.includes('"\'=HYPERLINK(""x"")"'));
});
test('all public collection references resolve and private ones are absent',()=>{
 const ids=new Set(records.map(r=>r.id));const images=new Set(records.flatMap(r=>r.images.map(i=>i.id)));
 assert.equal(ids.size,records.length);
 for(const c of data.collections){for(const id of c.recordIds)assert.ok(ids.has(id));for(const id of c.imageIds)assert.ok(images.has(id));}
 assert.deepEqual(data.collections.filter(c=>c.origin==='public').map(c=>c.id),['public-1']);
});
