import {el,node,link,option,source,fail,download} from './dom.mjs';
import {compare,selection} from './model.mjs';
const params=new URLSearchParams(location.search);
let data,shown=[];
function address(url) {
  if(!url) return node('td','—');
  const address=new URL(url), cell=node('td',undefined,'wrap');
  cell.append(link(address.hostname+address.pathname,url));return cell;
}
function render(){
  const before=data.editions.find(e=>e.date===el('from').value), after=data.editions.find(e=>e.date===el('to').value);
  for(const o of el('from').options)o.disabled=o.value>after.date;
  for(const o of el('to').options)o.disabled=o.value<before.date;
  shown=selection(compare(before.rows,after.rows),el('mode').value,el('query').value);
  el('summary').textContent=shown.length+' matching institutions · '+Object.keys(before.rows).length+' earlier entries · '+Object.keys(after.rows).length+' later entries.';
  el('sources').replaceChildren(link('Read earlier directory ↗',before.source.replace('id_/','/')),link('Read later directory ↗',after.source.replace('id_/','/')));
  const output=shown.map(r=>{const tr=node('tr');tr.append(node('th',r.name),node('td',r.hostChanged?'Hostname changed':r.state),address(r.old),address(r.current));return tr});
  el('rows').replaceChildren(...output);
  const url=new URL(location.href);for(const k of ['from','to','mode'])url.searchParams.set(k,el(k).value);
  url.searchParams.set('q',el('query').value);history.replaceState(null,'',url);
}
async function start(){
  data=await source();const editions=data.editions;
  for(const id of ['from','to'])for(const edition of editions)option(id,edition.date,edition.date);
  const valid=d=>editions.some(e=>e.date===d);
  const last=editions.at(-1);el('to').value=valid(params.get('to'))?params.get('to'):last.date;
  const previous=editions.filter(e=>e.date<el('to').value).at(-1)??editions[0];
  el('from').value=valid(params.get('from'))&&params.get('from')<=el('to').value?params.get('from'):previous.date;
  el('query').value=params.get('q')??'';
  if([...el('mode').options].some(o=>o.value===params.get('mode')))el('mode').value=params.get('mode');
  for(const id of ['from','to','mode','query'])el(id).addEventListener(id==='query'?'input':'change',render);
  el('status').textContent=editions.length+' saved directory editions · Current directory checked '+data.retrieved;
  el('certs').replaceChildren(...Object.entries(data.certificates).map(([host,group])=>{
    const card=node('article');card.append(node('h3',host,'wrap'),node('p',group.count+' reported issuances','strong'),node('p',Object.entries(group.issuers).map(([name,n])=>name+' ('+n+')').join(', ')||'No issuer listed.'),node('small','Retrieved '+group.date));return card;
  }));
  el('csv').onclick=()=>download('directory-changes.csv',['Institution','Change','Earlier edition','Earlier URL','Later edition','Later URL'],shown.map(r=>[r.name,r.state,el('from').value,r.old,el('to').value,r.current]));
  render();
}
start().catch(fail);
