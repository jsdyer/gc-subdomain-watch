export function compare(earlier,later) {
  return [...new Set([...Object.keys(earlier),...Object.keys(later)])].sort((a,b)=>a.localeCompare(b,'en-CA')).map(name=>{
    const old=earlier[name]??'', current=later[name]??'';
    const state=!old?'Added':!current?'Removed':old===current?'Unchanged':'Destination changed';
    const hostChanged=Boolean(old&&current&&new URL(old).hostname!==new URL(current).hostname);
    return {name,old,current,state,hostChanged};
  });
}
export function selection(rows,mode,query) {
  const text=query.trim().toLowerCase();
  return rows.filter(r=>(mode==='All'||mode==='Changes'&&r.state!=='Unchanged'||r.state===mode||mode==='Hostname changed'&&r.hostChanged) &&
    [r.name,r.old,r.current].some(s=>s.toLowerCase().includes(text)));
}
