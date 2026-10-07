from pathlib import Path
from html import escape
import json, re, yaml

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"_site"
COMP=OUT/"companies"
OUT.mkdir(exist_ok=True)
COMP.mkdir(exist_ok=True)

def slugify(s):
    s=re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
    return s or "company"

def status_label(s):
    return {
        "verified":"Verified location",
        "provided_unverified":"Provided · not reverified",
        "approximate":"Approximate location",
        "unresolved":"Location unresolved",
    }.get(s,s)

companies=[]
used={}
for path in sorted((ROOT/"companies").glob("*.yml")):
    c=yaml.safe_load(path.read_text(encoding="utf-8"))
    base=slugify(c["name"])
    used[base]=used.get(base,0)+1
    c["_slug"]=base if used[base]==1 else f"{base}-{used[base]}"
    evtypes=sorted({e.get("type") for e in c.get("evidence",[]) if e.get("type")})
    c["_evidence_types"]=evtypes
    c["_has_job_evidence"]="job_post" in evtypes or "careers" in evtypes
    c["_has_linkedin_employee"]="linkedin_employee" in evtypes
    c["_apply_ready"]=bool(c.get("careers_url") or c.get("hr_email"))
    companies.append(c)

companies.sort(key=lambda c:c["name"].casefold())

def esc(x): return escape("" if x is None else str(x), quote=True)
def jsdata(x): return json.dumps(x,ensure_ascii=False).replace("</","<\\/")

CSS=r"""
:root{--bg:#f4f6f7;--surface:#fff;--surface2:#eef2f3;--ink:#172129;--muted:#61707b;--line:#d6dee2;--strong:#9eabb3;--accent:#006d5b;--accent2:#dff1ec;--warn:#9b5b00;--warnbg:#fff0d8;--bad:#8b3d35;--badbg:#fae8e6;--link:#05639d}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--link);text-underline-offset:3px}.wrap{width:min(1480px,100%);margin:auto;padding:24px clamp(14px,3vw,38px) 60px}.hero{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(280px,.6fr);gap:24px;align-items:end;padding:12px 0 25px}.eyebrow{text-transform:uppercase;letter-spacing:.09em;font-size:11px;color:var(--accent);font-weight:800}.hero h1{font-size:clamp(34px,5vw,64px);line-height:1;letter-spacing:-.045em;margin:7px 0 12px}.hero p{max-width:780px;color:var(--muted);font-size:17px;margin:0}.stats{display:grid;grid-template-columns:repeat(2,1fr);border:1px solid var(--line);background:var(--surface)}.stat{padding:15px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.stat:nth-child(2n){border-right:0}.stat:nth-last-child(-n+2){border-bottom:0}.stat b{display:block;font-size:24px}.stat span{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.filters{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:blur(10px);border:1px solid var(--line);padding:14px;box-shadow:0 10px 30px rgba(23,33,41,.06)}.filter-grid{display:grid;grid-template-columns:minmax(240px,2fr) repeat(5,minmax(130px,1fr));gap:9px}.field label{display:block;font-size:10px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:5px}.field input,.field select,.multi summary{width:100%;min-height:40px;border:1px solid var(--strong);background:var(--surface);color:var(--ink);padding:8px 10px;border-radius:4px}.multi{position:relative}.multi summary{cursor:pointer;list-style:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.multi summary::-webkit-details-marker{display:none}.menu{position:absolute;z-index:10;top:44px;left:0;width:min(330px,80vw);background:var(--surface);border:1px solid var(--strong);box-shadow:0 16px 35px rgba(0,0,0,.14);padding:9px}.menu input{width:100%;min-height:36px;border:1px solid var(--line);padding:7px;margin-bottom:6px}.options{max-height:235px;overflow:auto}.opt{display:flex;gap:8px;align-items:center;padding:5px;font-size:12px}.opt input{width:auto;min-height:0;margin:0}.filters2{display:grid;grid-template-columns:repeat(4,minmax(140px,1fr)) auto;gap:9px;margin-top:9px}.quick{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}.quick button,.clear{border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:7px 10px;cursor:pointer;font-size:12px}.quick button.on{background:var(--accent2);border-color:var(--accent);color:var(--accent)}.clear{border-radius:4px;font-weight:700}.summary{display:flex;justify-content:space-between;gap:14px;align-items:baseline;margin:23px 0 9px}.summary h2{margin:0;font-size:20px}.summary span{color:var(--muted);font-size:12px}.results{border-top:2px solid var(--ink)}.card{display:grid;grid-template-columns:minmax(230px,1.25fr) minmax(170px,.8fr) minmax(200px,1fr) minmax(240px,1.25fr) minmax(170px,.75fr);gap:16px;padding:17px 12px;background:var(--surface);border-bottom:1px solid var(--line);align-items:start}.card:hover{background:#fbfcfc}.name{font-weight:800;font-size:17px;line-height:1.25}.muted{color:var(--muted)}.small{font-size:12px}.chips{display:flex;gap:5px;flex-wrap:wrap}.chip{font-size:10px;background:var(--surface2);padding:4px 6px;border-radius:3px}.chip.green{background:var(--accent2);color:var(--accent)}.chip.warn{background:var(--warnbg);color:var(--warn)}.chip.bad{background:var(--badbg);color:var(--bad)}.actions{display:flex;gap:6px;flex-wrap:wrap}.btn{display:inline-block;text-decoration:none;border:1px solid var(--line);padding:6px 8px;border-radius:3px;font-size:11px;font-weight:700}.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}.evidence{margin-top:8px}.evidence summary{cursor:pointer;color:var(--link);font-size:11px;font-weight:700}.evidence ul{margin:8px 0 0;padding-left:18px;font-size:11px}.empty{padding:50px;text-align:center;background:var(--surface);color:var(--muted)}.profile{max-width:1100px;margin:25px auto;padding:0 18px}.back{display:inline-block;margin-bottom:15px}.panel{background:var(--surface);border:1px solid var(--line);padding:18px;margin-bottom:14px}.panel h1{margin:0 0 5px;font-size:32px}.panel h2{font-size:15px;margin:0 0 10px}.description{font-size:16px;line-height:1.65;margin:0;max-width:920px}.kv{display:grid;grid-template-columns:170px 1fr;gap:7px 14px}.kv>:nth-child(odd){color:var(--muted)}table{width:100%;border-collapse:collapse;font-size:12px}th,td{text-align:left;vertical-align:top;padding:8px;border-bottom:1px solid var(--line)}th{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.05em}
@media(max-width:1050px){.filter-grid{grid-template-columns:repeat(3,1fr)}.field.search{grid-column:1/-1}.filters2{grid-template-columns:repeat(3,1fr)}.card{grid-template-columns:1.2fr 1fr 1fr}.card .wide{grid-column:1/-1}}
@media(max-width:720px){.wrap{padding:12px}.hero{grid-template-columns:1fr}.filters{position:static}.filter-grid,.filters2{grid-template-columns:1fr 1fr}.field.search{grid-column:1/-1}.card{grid-template-columns:1fr}.card .wide{grid-column:auto}.kv{grid-template-columns:1fr}.kv>:nth-child(odd){font-weight:700}}
"""

def location_chip(c):
    s=(c.get("location") or {}).get("status")
    cls="green" if s=="verified" else "bad" if s=="unresolved" else "warn"
    return f'<span class="chip {cls}">{esc(status_label(s))}</span>'

def company_description(c):
    if c.get("description"):
        return c["description"]
    industry = c.get("industry") or "an unclassified sector"
    return f"{c['name']} is currently classified in the source dataset as {industry}. A fuller description will be added when this company is individually verified."

def company_profile(c):
    loc=c.get("location") or {}
    evrows=[]
    for e in c.get("evidence",[]):
        ref=e.get("url") or e.get("reference") or ""
        shown=(f'<a href="{esc(ref)}" rel="nofollow noopener">{esc(ref)}</a>' if e.get("url") else esc(ref))
        evrows.append(f"<tr><td>{esc(e.get('type'))}</td><td>{shown}</td><td>{esc(e.get('label'))}</td></tr>")
    actions=[]
    if c.get("careers_url"): actions.append(f'<a class="btn primary" href="{esc(c["careers_url"])}">Careers / apply</a>')
    if c.get("website"): actions.append(f'<a class="btn" href="{esc(c["website"])}">Website</a>')
    if c.get("linkedin"): actions.append(f'<a class="btn" href="{esc(c["linkedin"])}">LinkedIn</a>')
    if c.get("hr_email"): actions.append(f'<a class="btn" href="mailto:{esc(c["hr_email"])}">Email HR</a>')
    if loc.get("maps_url"): actions.append(f'<a class="btn" href="{esc(loc["maps_url"])}">Google Maps</a>')
    tech="".join(f'<span class="chip">{esc(x)}</span>' for x in c.get("technologies",[])) or '<span class="muted">No public stack evidence</span>'
    cats="".join(f'<span class="chip green">{esc(x)}</span>' for x in c.get("categories",[])) or '<span class="muted">No categories</span>'
    sig="".join(f'<span class="chip green">{esc(x)}</span>' for x in (c.get("job_seeker") or {}).get("signals",[])) or '<span class="muted">No explicit early-career signal found in stored research</span>'
    description=company_description(c)
    body=f"""<div class="profile"><a class="back" href="../index.html">← All employers</a>
<section class="panel"><div class="eyebrow">Employer evidence profile</div><h1>{esc(c["name"])}</h1><div class="muted">{esc(c.get("industry") or "Industry not classified")}</div><div class="actions" style="margin-top:14px">{''.join(actions)}</div></section>
<section class="panel"><h2>What the company does</h2><p class="description">{esc(description)}</p></section>
<section class="panel"><h2>Job-seeker snapshot</h2><div class="kv">
<div>Reported city / area</div><div>{esc(loc.get("area") or "Unresolved")} {location_chip(c)}</div>
<div>Address</div><div>{esc(loc.get("address") or "Not publicly resolved")}</div>
<div>Company size</div><div>{esc(c.get("size") or "Not listed")}</div>
<div>HR contact</div><div>{('<a href="mailto:'+esc(c['hr_email'])+'">'+esc(c['hr_email'])+'</a>') if c.get('hr_email') else 'Not publicly listed'}</div>
<div>Early-career signals</div><div>{sig}</div>
</div></section>
<section class="panel"><h2>Categories</h2><div class="chips">{cats}</div><h2 style="margin-top:17px">Technology evidence</h2><div class="chips">{tech}</div></section>
<section class="panel"><h2>Research notes</h2><p>{esc(c.get("notes") or "No additional research note.")}</p></section>
<section class="panel"><h2>Evidence</h2><table><thead><tr><th>Type</th><th>Reference</th><th>Use</th></tr></thead><tbody>{''.join(evrows)}</tbody></table></section>
</div>"""
    return page(c["name"],body)

def page(title,body):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><style>{CSS}</style></head><body>{body}</body></html>'

public=[]
for c in companies:
    p=dict(c)
    public.append(p)
    (COMP/f'{c["_slug"]}.html').write_text(company_profile(c),encoding="utf-8")

areas=sorted({(c.get("location") or {}).get("area") for c in companies if (c.get("location") or {}).get("area")})
industries=sorted({c.get("industry") for c in companies if c.get("industry")})
categories=sorted({x for c in companies for x in c.get("categories",[])})
technologies=sorted({x for c in companies for x in c.get("technologies",[])})
evidence_types=sorted({x for c in companies for x in c.get("_evidence_types",[])})
verified=sum(1 for c in companies if (c.get("location") or {}).get("status")=="verified")
careers=sum(1 for c in companies if c.get("careers_url"))
early=sum(1 for c in companies if (c.get("job_seeker") or {}).get("early_career_signal"))

def options(items):
    return "".join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in items)

body=f"""<main class="wrap">
<section class="hero"><div><div class="eyebrow">Jordan · evidence-first employer research</div><h1>Find employers worth applying to.</h1><p>Search 500 companies by role-relevant technology, sector, location confidence, application path and the evidence behind each claim.</p></div>
<div class="stats"><div class="stat"><b>{len(companies)}</b><span>Employers</span></div><div class="stat"><b>{verified}</b><span>Verified locations</span></div><div class="stat"><b>{careers}</b><span>Career links</span></div><div class="stat"><b>{early}</b><span>Early-career signals</span></div></div></section>
<section class="filters">
<div class="filter-grid">
<div class="field search"><label>Search</label><input id="q" type="search" placeholder="Company, Java, fintech, address, evidence…"></div>
<div class="field"><label>Reported city / area</label><select id="area"><option value="">All areas</option>{options(areas)}</select></div>
<div class="field"><label>Industry</label><select id="industry"><option value="">All industries</option>{options(industries)}</select></div>
<div class="field"><label>Location confidence</label><select id="locstatus"><option value="">Any status</option><option value="verified">Verified</option><option value="provided_unverified">Provided · not reverified</option><option value="approximate">Approximate</option><option value="unresolved">Unresolved</option></select></div>
<div class="field"><label>HR email</label><select id="hr"><option value="">Any</option><option value="yes">Available</option><option value="no">Not listed</option></select></div>
<div class="field"><label>Careers page</label><select id="careers"><option value="">Any</option><option value="yes">Available</option><option value="no">Not listed</option></select></div>
</div>
<div class="filters2">
<div class="field"><label>Evidence type</label><select id="evidence"><option value="">Any evidence</option>{options(evidence_types)}</select></div>
<div class="field"><label>Category</label><details class="multi" id="catBox"><summary id="catSummary">All categories</summary><div class="menu"><input class="option-search" data-target="catOptions" placeholder="Search categories"><div class="options" id="catOptions"></div></div></details></div>
<div class="field"><label>Technology</label><details class="multi" id="techBox"><summary id="techSummary">All technologies</summary><div class="menu"><input class="option-search" data-target="techOptions" placeholder="Search technologies"><div class="options" id="techOptions"></div></div></details></div>
<div class="field"><label>Sort</label><select id="sort"><option value="evidence">Evidence coverage</option><option value="apply">Application readiness</option><option value="name">Company name</option></select></div>
<button class="clear" id="clear">Clear filters</button>
</div>
<div class="quick"><button data-quick="apply">Application ready</button><button data-quick="early">Intern / junior / graduate signal</button><button data-quick="jobs">Job-post evidence</button><button data-quick="employee">LinkedIn employee evidence</button><button data-quick="verified">Verified location</button></div>
</section>
<div class="summary"><h2 id="count">{len(companies)} employers</h2><span>Location confidence is shown separately from city/area.</span></div>
<section class="results" id="results"></section>
</main>
<script id="data" type="application/json">{jsdata(public)}</script>
<script>
(function(){{
const DATA=JSON.parse(document.getElementById('data').textContent);
const state={{cats:new Set(),tech:new Set(),quick:new Set()}};
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const statusLabel=s=>({{verified:'Verified',provided_unverified:'Provided · not reverified',approximate:'Approximate',unresolved:'Unresolved'}}[s]||s);
const statusClass=s=>s==='verified'?'green':s==='unresolved'?'bad':'warn';

function fillChecks(id,items,set,summaryId,label){{
  const box=$(id); box.innerHTML='';
  items.forEach(v=>{{const l=document.createElement('label');l.className='opt';l.innerHTML='<input type="checkbox" value="'+esc(v)+'"> <span>'+esc(v)+'</span>';const cb=l.querySelector('input');cb.addEventListener('change',()=>{{cb.checked?set.add(v):set.delete(v);$(summaryId).textContent=set.size?set.size+' '+label+' selected':'All '+label;render();}});box.appendChild(l);}});
}}
fillChecks('catOptions',{json.dumps(categories,ensure_ascii=False)},state.cats,'catSummary','categories');
fillChecks('techOptions',{json.dumps(technologies,ensure_ascii=False)},state.tech,'techSummary','technologies');

document.querySelectorAll('.option-search').forEach(inp=>inp.addEventListener('input',()=>{{const q=inp.value.toLowerCase();document.querySelectorAll('#'+inp.dataset.target+' .opt').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(q));}}));
['q','area','industry','locstatus','hr','careers','evidence','sort'].forEach(id=>$(id).addEventListener(id==='q'?'input':'change',render));
document.querySelectorAll('[data-quick]').forEach(b=>b.addEventListener('click',()=>{{const k=b.dataset.quick;state.quick.has(k)?state.quick.delete(k):state.quick.add(k);b.classList.toggle('on',state.quick.has(k));render();}}));
$('clear').addEventListener('click',()=>{{['q','area','industry','locstatus','hr','careers','evidence'].forEach(id=>$(id).value='');$('sort').value='evidence';state.cats.clear();state.tech.clear();state.quick.clear();document.querySelectorAll('.opt input').forEach(x=>x.checked=false);document.querySelectorAll('[data-quick]').forEach(x=>x.classList.remove('on'));$('catSummary').textContent='All categories';$('techSummary').textContent='All technologies';render();}});

function match(c){{
  const q=$('q').value.trim().toLowerCase(), loc=c.location||{{}}, ev=c._evidence_types||[];
  if(q){{const hay=[c.name,c.industry,c.description,c.notes,loc.area,loc.address,...(c.categories||[]),...(c.technologies||[]),...ev].filter(Boolean).join(' ').toLowerCase();if(!hay.includes(q))return false;}}
  if($('area').value && loc.area!==$('area').value)return false;
  if($('industry').value && c.industry!==$('industry').value)return false;
  if($('locstatus').value && loc.status!==$('locstatus').value)return false;
  if($('hr').value==='yes'&&!c.hr_email)return false;if($('hr').value==='no'&&c.hr_email)return false;
  if($('careers').value==='yes'&&!c.careers_url)return false;if($('careers').value==='no'&&c.careers_url)return false;
  if($('evidence').value&&!ev.includes($('evidence').value))return false;
  if(state.cats.size && ![...state.cats].some(x=>(c.categories||[]).includes(x)))return false;
  if(state.tech.size && ![...state.tech].some(x=>(c.technologies||[]).includes(x)))return false;
  if(state.quick.has('apply')&&!c._apply_ready)return false;
  if(state.quick.has('early')&&!(c.job_seeker||{{}}).early_career_signal)return false;
  if(state.quick.has('jobs')&&!c._has_job_evidence)return false;
  if(state.quick.has('employee')&&!c._has_linkedin_employee)return false;
  if(state.quick.has('verified')&&loc.status!=='verified')return false;
  return true;
}}
function evidenceScore(c){{return new Set((c.evidence||[]).map(e=>e.type)).size;}}
function card(c){{
 const loc=c.location||{{}}, sig=(c.job_seeker||{{}}).signals||[], tech=(c.technologies||[]).slice(0,8), cats=(c.categories||[]).slice(0,5);
 const acts=['<a class="btn primary" href="companies/'+c._slug+'.html">Evidence profile</a>'];
 if(c.careers_url)acts.push('<a class="btn" href="'+esc(c.careers_url)+'">Apply</a>'); else if(c.website)acts.push('<a class="btn" href="'+esc(c.website)+'">Website</a>');
 if(c.hr_email)acts.push('<a class="btn" href="mailto:'+esc(c.hr_email)+'">Email HR</a>');
 const ev=(c.evidence||[]).slice(0,6).map(e=>'<li><b>'+esc(e.type)+'</b> · '+(e.url?'<a href="'+esc(e.url)+'" rel="nofollow noopener">'+esc(e.label||e.url)+'</a>':esc(e.reference||e.label||''))+'</li>').join('');
 return '<article class="card"><div><div class="name">'+esc(c.name)+'</div><div class="muted small">'+esc(c.size||'Size not listed')+'</div><div class="chips" style="margin-top:8px">'+cats.map(x=>'<span class="chip green">'+esc(x)+'</span>').join('')+'</div></div>'+
 '<div><b>'+esc(c.industry||'Industry not classified')+'</b><div class="chips" style="margin-top:8px">'+sig.map(x=>'<span class="chip green">'+esc(x)+'</span>').join('')+'</div></div>'+
 '<div><b>'+esc(loc.area||'Unresolved')+'</b><div class="small muted">'+esc(loc.address||'No exact public address')+'</div><div class="chips" style="margin-top:7px"><span class="chip '+statusClass(loc.status)+'">'+esc(statusLabel(loc.status))+'</span></div></div>'+
 '<div class="wide"><div class="chips">'+tech.map(x=>'<span class="chip">'+esc(x)+'</span>').join('')+'</div><details class="evidence"><summary>'+evidenceScore(c)+' evidence types · '+(c.evidence||[]).length+' references</summary><ul>'+ev+'</ul></details></div>'+
 '<div><div class="actions">'+acts.join('')+'</div></div></article>';
}}
function render(){{
 let rows=DATA.filter(match), sort=$('sort').value;
 rows.sort((a,b)=>sort==='name'?a.name.localeCompare(b.name):sort==='apply'?((b._apply_ready?1:0)-(a._apply_ready?1:0)||evidenceScore(b)-evidenceScore(a)||a.name.localeCompare(b.name)):(evidenceScore(b)-evidenceScore(a)||a.name.localeCompare(b.name)));
 $('count').textContent=rows.length+' employers';
 $('results').innerHTML=rows.length?rows.map(card).join(''):'<div class="empty"><b>No employers match these filters.</b><div>Clear or broaden one of the filters.</div></div>';
}}
render();
}})();
</script>"""

(OUT/"index.html").write_text(page("Jordan Job Employers Index",body),encoding="utf-8")
(OUT/"companies.json").write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/".nojekyll").write_text("",encoding="utf-8")
print(f"Built {len(companies)} employer pages.")
