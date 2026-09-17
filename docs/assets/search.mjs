export const fields = {Titulo:'Título',Materias6XX:'Todas las materias',Persona:'Persona · 600',Entidad:'Entidad · 610',Evento:'Evento · 611',Titulo630:'Título uniforme · 630',Tema650:'Tema · 650',Lugar:'Lugar · 651',Genero655:'Género / forma · 655',Anio:'Año',Barcode:'Barcode',NroOriginal:'Número original'};
export const marc = {'600':'Personas','610':'Entidades','611':'Eventos','630':'Títulos uniformes','650':'Temas','651':'Lugares','655':'Género / forma'};
export const norm = s => String(s ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('es').replace(/\s+/g,' ').trim();
export const contains = (s,q) => norm(s).includes(norm(q));
export function basic(r,q) { return contains(r.title,q) || r.subjects.some(s=>contains(s.term,q)); }
export function condition(r,c) {
  const map={Persona:'600',Entidad:'610',Evento:'611',Titulo630:'630',Tema650:'650',Lugar:'651',Genero655:'655'};
  let match=false;
  if (map[c.field]) match=r.subjects.some(s=>s.field===map[c.field] && contains(s.term,c.term));
  else if (c.field==='Materias6XX') match=r.subjects.some(s=>contains(s.term,c.term));
  else if(c.field==='Titulo') match=contains(r.title,c.term);
  else if(c.field==='Anio') match=contains(r.date.slice(0,4),c.term);
  else if(c.field==='Barcode') match=contains(r.id,c.term);
  else if(c.field==='NroOriginal') match=contains(r.originalNumber,c.term);
  return c.not ? !match : match;
}
export function advanced(r,rows) {
  const active=rows.filter(c=>String(c.term ?? '').trim());
  if(!active.length) return true;
  return active.slice(1).reduce((acc,c)=>c.op==='OR' ? acc || condition(r,c) : acc && condition(r,c), condition(r,active[0]));
}
export const hasImage = r => r.images.some(i=>Boolean(i.src));
export function search(records,params={},rows=[]) {
 return records.filter(r=> (!params.q || basic(r,params.q)) && advanced(r,rows)
  && (!params.field || r.subjects.some(s=>s.field===params.field && s.term===params.term))
  && (!params.refine || contains([r.title,r.id,r.sys,r.date,...r.subjects.map(s=>s.term)].join(' '),params.refine))
  && (!params.from || (r.date.slice(0,4)>='1000' && r.date.slice(0,4)>=params.from))
  && (!params.to || (r.date.slice(0,4)>='1000' && r.date.slice(0,4)<=params.to))
  && (!params.images || hasImage(r)));
}
export function terms(records,field) {
 const map=new Map();
 for (const r of records) for (const term of new Set(r.subjects.filter(s=>s.field===field).map(s=>s.term))) {
   if(!map.has(term)) map.set(term,{term,count:0,digital:false});
   const row=map.get(term); row.count++; row.digital ||= hasImage(r);
 }
 return [...map.values()].sort((a,b)=>a.term.localeCompare(b.term,'es',{sensitivity:'base'}));
}
export function safeCsv(value) {
 let s=String(value??''); if (/^[\s]*[=+@-]/.test(s)) s="'"+s;
 return '"'+s.replaceAll('"','""')+'"';
}
export function csv(records) {
 const rows=[['SYS BN','Título','Barcode','Fecha','Materias'],...records.map(r=>[r.sys,r.title,r.id,r.date,r.subjects.map(s=>s.term).join(' | ')])];
 return '\uFEFF'+rows.map(row=>row.map(safeCsv).join(';')).join('\r\n');
}
