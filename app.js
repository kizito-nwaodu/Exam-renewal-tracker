
(function(){
  const STORAGE_KEY = 'msftExamTracker.v1';
  const $ = sel => document.querySelector(sel);

  // Seed data (verify against your transcript)
  const seed = [
    {id:crypto.randomUUID(), level:'Associate', name:'Microsoft Endpoint Administrator Associate', codes:'MD-102', status:'Passed (Active)', datePassed:'', expiration:'', renewal:12, domain:'Endpoint Management', source:'https://learn.microsoft.com/certifications/exams/md-102/', notes:'Pre-filled; verify against transcript.'},
    {id:crypto.randomUUID(), level:'Associate', name:'Security Operations Analyst Associate', codes:'SC-200', status:'Passed (Active)', datePassed:'', expiration:'', renewal:12, domain:'Security / XDR', source:'https://learn.microsoft.com/certifications/exams/sc-200/', notes:'Pre-filled; verify against transcript.'},
    {id:crypto.randomUUID(), level:'Associate', name:'Identity and Access Administrator Associate', codes:'SC-300', status:'Passed (Active)', datePassed:'', expiration:'', renewal:12, domain:'Entra ID / IAM', source:'https://learn.microsoft.com/certifications/exams/sc-300/', notes:'Pre-filled; verify against transcript.'},
    {id:crypto.randomUUID(), level:'Associate', name:'Information Protection Administrator Associate', codes:'SC-400', status:'Passed (Active)', datePassed:'', expiration:'', renewal:12, domain:'Purview / Compliance', source:'https://learn.microsoft.com/certifications/exams/sc-400/', notes:'Pre-filled; verify against transcript.'},
    {id:crypto.randomUUID(), level:'Associate', name:'Designing and Implementing Microsoft Security (placeholder)', codes:'SC-401', status:'Passed (Active)', datePassed:'', expiration:'', renewal:12, domain:'Security / Design', source:'https://learn.microsoft.com/certifications/', notes:'Verify exact title/cert mapping on Learn.'}
  ];

  const state = { items: load() ?? seed, editingId: null };

  function load(){ try{ return JSON.parse(localStorage.getItem(STORAGE_KEY)); }catch{ return null } }
  function save(){ localStorage.setItem(STORAGE_KEY, JSON.stringify(state.items)); }

  function summarize(){
    const c = {
      total: state.items.length,
      planned: state.items.filter(x=>x.status==='Planned').length,
      scheduled: state.items.filter(x=>x.status==='Scheduled').length,
      active: state.items.filter(x=>x.status==='Passed (Active)').length,
      expired: state.items.filter(x=>x.status==='Passed (Expired)').length,
      retired: state.items.filter(x=>x.status==='Retired').length,
    };
    document.getElementById('summary').innerHTML = `
      <div class="card"><h4>Total</h4><div class="num">${c.total}</div></div>
      <div class="card"><h4>Active</h4><div class="num">${c.active}</div></div>
      <div class="card"><h4>Scheduled</h4><div class="num">${c.scheduled}</div></div>
      <div class="card"><h4>Expired</h4><div class="num">${c.expired}</div></div>
      <div class="card"><h4>Retired</h4><div class="num">${c.retired}</div></div>`;
  }

  function daysUntil(dateStr){ if(!dateStr) return null; const d=new Date(dateStr); if(isNaN(d)) return null; const t=new Date(); return Math.ceil((d-t)/(1000*60*60*24)); }

  function badgeForExpiration(item){
    const left = daysUntil(item.expiration);
    if(left === null) return '';
    const label = left >= 0 ? `${left} days` : `${Math.abs(left)} days ago`;
    const cls = left < 0 ? 'danger' : (left <= 60 ? 'warn' : 'ok');
    return `<span class="badge ${cls}">${label}</span>`;
  }

  function applyFilters(items){
    let filtered = items.slice();
    const q = document.getElementById('searchInput').value.trim().toLowerCase();
    if(q){ filtered = filtered.filter(x => `${x.name} ${x.codes} ${x.domain}`.toLowerCase().includes(q)); }
    const levelSel = document.getElementById('levelFilter');
    const levels = Array.from(levelSel.selectedOptions).map(o=>o.value);
    if(levels.length){ filtered = filtered.filter(x=>levels.includes(x.level)); }
    const statusSel = document.getElementById('statusFilter');
    const statuses = Array.from(statusSel.selectedOptions).map(o=>o.value);
    if(statuses.length){ filtered = filtered.filter(x=>statuses.includes(x.status)); }
    const sort = document.getElementById('sortSelect').value;
    filtered.sort((a,b)=>{
      if(sort==='name') return a.name.localeCompare(b.name);
      if(sort==='code') return (a.codes||'').localeCompare(b.codes||'');
      if(sort==='datePassed') return new Date(b.datePassed||0) - new Date(a.datePassed||0);
      if(sort==='expiration') return new Date(a.expiration||8640000000000000) - new Date(b.expiration||8640000000000000);
      return 0;
    });
    return filtered;
  }

  function render(){
    summarize();
    const tbody = document.getElementById('gridBody');
    tbody.innerHTML = '';
    const list = applyFilters(state.items);
    for(const item of list){
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><span class="badge">${item.level||''}</span></td>
        <td>${item.name||''}</td>
        <td>${item.codes||''}</td>
        <td>${item.status||''}</td>
        <td>${item.datePassed||''}</td>
        <td>${item.expiration||''}</td>
        <td>${badgeForExpiration(item)}</td>
        <td>${item.domain||''}</td>
        <td>${item.source?`<a href="${item.source}" target="_blank">link</a>`:''}</td>
        <td class="actions">
          <button class="btn" data-edit="${item.id}">Edit</button>
          <button class="btn danger" data-del="${item.id}">Delete</button>
        </td>`;
      tbody.appendChild(tr);
    }
  }

  function openDialog(editId){
    state.editingId = editId ?? null;
    const isEdit = !!editId;
    document.getElementById('dlgTitle').textContent = isEdit ? 'Edit Item' : 'Add Certification/Exam';
    const data = isEdit ? state.items.find(x=>x.id===editId) : {level:'Associate', status:'Planned', renewal:12};
    document.getElementById('name').value = data.name || '';
    document.getElementById('codes').value = data.codes || '';
    document.getElementById('level').value = data.level || 'Associate';
    document.getElementById('status').value = data.status || 'Planned';
    document.getElementById('datePassed').value = data.datePassed || '';
    document.getElementById('expiration').value = data.expiration || '';
    document.getElementById('renewal').value = data.renewal ?? 12;
    document.getElementById('domain').value = data.domain || '';
    document.getElementById('source').value = data.source || '';
    document.getElementById('notes').value = data.notes || '';
    document.getElementById('itemDialog').showModal();
  }

  function saveDialog(){
    const payload = {
      id: state.editingId ?? crypto.randomUUID(),
      name: document.getElementById('name').value.trim(),
      codes: document.getElementById('codes').value.trim(),
      level: document.getElementById('level').value,
      status: document.getElementById('status').value,
      datePassed: document.getElementById('datePassed').value,
      expiration: document.getElementById('expiration').value,
      renewal: +(document.getElementById('renewal').value||0),
      domain: document.getElementById('domain').value.trim(),
      source: document.getElementById('source').value.trim(),
      notes: document.getElementById('notes').value.trim(),
    };
    if(!payload.name) return;
    if(state.editingId){
      const idx = state.items.findIndex(x=>x.id===state.editingId);
      if(idx>-1) state.items[idx] = payload;
    } else {
      state.items.unshift(payload);
    }
    save();
    render();
    document.getElementById('itemDialog').close();
  }

  function delItem(id){ state.items = state.items.filter(x=>x.id!==id); save(); render(); }

  function exportData(){
    const blob = new Blob([JSON.stringify(state.items, null, 2)], {type:'application/json'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'msft-exam-tracker.json';
    a.click();
  }

  async function importData(){
    const dlg = document.getElementById('importDialog');
    dlg.showModal();
    const cancel = ()=> dlg.close();
    document.getElementById('importCancel').onclick = cancel;
    document.getElementById('importConfirm').onclick = async ()=>{
      const fi = document.getElementById('fileInput');
      let text = '';
      if(fi.files && fi.files[0]){ text = await fi.files[0].text(); } else { text = document.getElementById('pasteArea').value.trim(); }
      if(!text){ cancel(); return; }
      try{
        if(fi.files && fi.files[0] && fi.files[0].name.endsWith('.csv')){
          const rows = csvToJson(text);
          mergeImported(rows);
        } else {
          const arr = JSON.parse(text);
          mergeImported(arr);
        }
        save(); render(); cancel();
      }catch(e){ alert('Import failed: '+e.message); }
    };
  }

  function csvToJson(csv){
    const lines = csv.split(/?
/).filter(Boolean);
    const headers = lines.shift().split(',').map(h=>h.trim());
    return lines.map(l=>{
      const cols = l.split(',');
      const obj = {}; headers.forEach((h,i)=> obj[h] = (cols[i]||'').trim());
      return normalize(obj);
    });
  }

  function normalize(obj){
    const map = (o,k,alts=[])=> o[k] ?? alts.map(a=>o[a]).find(v=>v!==undefined);
    return {
      id: crypto.randomUUID(),
      name: map(obj,'Certification / Exam Name',['Name','Title']) || '',
      codes: map(obj,'Exam Code(s)',['Code','Exam']) || '',
      level: map(obj,'Level',[]) || 'Associate',
      status: map(obj,'Status',[]) || 'Planned',
      datePassed: map(obj,'Date Passed',[]) || '',
      expiration: map(obj,'Expiration Date',['Expiration']) || '',
      renewal: +(map(obj,'Renewal Due (months)',['Renewal']) || 12),
      domain: map(obj,'Role / Domain',['Domain','Role']) || '',
      source: map(obj,'Source Link',['Source']) || '',
      notes: map(obj,'Notes',[]) || ''
    };
  }

  // Events
  document.getElementById('addBtn').onclick = ()=> openDialog();
  document.getElementById('exportBtn').onclick = exportData;
  document.getElementById('importBtn').onclick = importData;
  document.getElementById('resetBtn').onclick = ()=>{ if(confirm('Clear all data in this browser?')){ localStorage.removeItem(STORAGE_KEY); state.items = []; render(); } };
  document.getElementById('itemForm').addEventListener('submit', (e)=>{ e.preventDefault(); saveDialog(); });
  document.getElementById('gridBody').addEventListener('click', (e)=>{
    const t = e.target; if(t.dataset.edit){ openDialog(t.dataset.edit); } if(t.dataset.del){ if(confirm('Delete this item?')) delItem(t.dataset.del); }
  });
  ['searchInput','levelFilter','statusFilter','sortSelect'].forEach(id=>{
    document.getElementById(id).addEventListener('input', render);
    document.getElementById(id).addEventListener('change', render);
  });

  render();
})();
