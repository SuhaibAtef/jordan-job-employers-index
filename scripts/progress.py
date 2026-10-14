"""Generate a verification progress page from the same YAML data as the employer index."""

from collections import Counter
from html import escape
from pathlib import Path
from urllib.parse import quote


def classify_status(company):
    """Company verification is independent of location verification."""
    value = str(company.get("verification_status") or "").strip().lower()
    return {
        "verified": ("verified", "Verified"),
        "partial": ("partial", "Partially verified"),
        "unresolved": ("unresolved", "Unresolved"),
    }.get(value, ("not_verified", "Not verified"))


def location_label(company):
    value = (company.get("location") or {}).get("status")
    return {
        "verified": "Verified location",
        "provided_unverified": "Provided, not verified",
        "approximate": "Approximate",
        "unresolved": "Unresolved",
    }.get(value, "Not recorded")


def esc(value):
    return escape("" if value is None else str(value), quote=True)


STYLE = """
:root{--bg:#f4f6f7;--surface:#fff;--ink:#172129;--muted:#61707b;--line:#d6dee2;--accent:#006d5b;--accent2:#dff1ec;--warn:#9b5b00;--warnbg:#fff0d8;--bad:#8b3d35;--badbg:#fae8e6;--link:#05639d}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
a{color:var(--link);text-underline-offset:3px}.wrap{max-width:1280px;margin:auto;padding:28px 22px 65px}.back{display:inline-block;margin-bottom:20px}
h1{font-size:clamp(30px,4vw,48px);line-height:1.1;margin:6px 0 12px;letter-spacing:-.035em}.eyebrow{font-size:11px;letter-spacing:.09em;font-weight:800;text-transform:uppercase;color:var(--accent)}.lead{font-size:16px;max-width:860px;color:var(--muted);margin:0 0 20px}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:20px 0}.stat{background:var(--surface);border:1px solid var(--line);padding:16px}.stat strong{display:block;font-size:29px;line-height:1.1}.stat span{color:var(--muted);font-size:12px}
.progress{height:13px;border-radius:20px;background:#d6dee2;overflow:hidden}.progress>div{height:100%;background:var(--accent)}.progress-text{color:var(--muted);font-size:12px;margin:7px 0 23px}
.controls{display:grid;grid-template-columns:minmax(230px,2fr) repeat(3,minmax(150px,1fr));gap:10px;background:var(--surface);border:1px solid var(--line);padding:14px}
label{display:block;font-size:11px;font-weight:700;color:var(--muted)}input,select{display:block;width:100%;min-height:42px;margin-top:5px;padding:8px 10px;background:#fff;border:1px solid #9eabb3;border-radius:4px;color:var(--ink);font:inherit}
.summary{display:flex;justify-content:space-between;gap:12px;align-items:baseline;margin:25px 0 9px}.summary h2{margin:0;font-size:19px}.summary span{color:var(--muted);font-size:12px}
.scroll{overflow-x:auto;border:1px solid var(--line);background:var(--surface)}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:800px}th,td{padding:11px 12px;text-align:left;vertical-align:middle;border-bottom:1px solid var(--line)}th{background:#eef2f3;color:#52616c;font-size:11px;letter-spacing:.03em;white-space:nowrap}tbody tr:hover{background:#f7faf9}tbody tr[hidden]{display:none}
.num{color:var(--muted);font-variant-numeric:tabular-nums}.company{font-weight:750}.industry{font-size:11px;color:var(--muted)}.pill{display:inline-block;font-size:11px;font-weight:700;padding:4px 8px;border-radius:999px;white-space:nowrap}
.verified{color:var(--accent);background:var(--accent2)}.partial{color:var(--warn);background:var(--warnbg)}.unresolved,.not_verified{color:var(--bad);background:var(--badbg)}
.note{color:var(--muted);font-size:12px;margin-top:14px;max-width:900px}
@media(max-width:780px){.wrap{padding:18px 12px 50px}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.controls{grid-template-columns:1fr 1fr}.controls label:first-child{grid-column:1/-1}}
@media(max-width:440px){.controls{grid-template-columns:1fr}.controls label:first-child{grid-column:auto}}
"""

SCRIPT = """
(function(){
  const rows=Array.from(document.querySelectorAll('#companyRows tr'));
  const search=document.getElementById('search');
  const status=document.getElementById('status');
  const location=document.getElementById('location');
  const sort=document.getElementById('sort');
  const count=document.getElementById('visibleCount');
  const tbody=document.getElementById('companyRows');
  function render(){
    const q=search.value.trim().toLocaleLowerCase();
    let shown=0;
    rows.forEach(row=>{
      const match=(!q || row.dataset.search.includes(q))
        && (!status.value || row.dataset.status===status.value)
        && (!location.value || row.dataset.location===location.value);
      row.hidden=!match;
      if(match)shown++;
    });
    const statusOrder={not_verified:0,unresolved:1,partial:2,verified:3};
    rows.sort((a,b)=>{
      if(sort.value==='status')return statusOrder[a.dataset.status]-statusOrder[b.dataset.status]||a.dataset.name.localeCompare(b.dataset.name);
      if(sort.value==='reviewed')return b.dataset.reviewed.localeCompare(a.dataset.reviewed)||a.dataset.name.localeCompare(b.dataset.name);
      return a.dataset.name.localeCompare(b.dataset.name);
    });
    rows.forEach(row=>tbody.appendChild(row));
    count.textContent=shown+' of '+rows.length+' employers';
  }
  [search,status,location,sort].forEach(el=>el.addEventListener(el===search?'input':'change',render));
  render();
})();
"""


def build_progress(companies, output_dir):
    """Write a complete, searchable verification table; all rows work without JS."""
    companies = sorted(companies, key=lambda c: c["name"].casefold())
    counts = Counter(classify_status(c)[0] for c in companies)
    total = len(companies)
    verified = counts["verified"]
    partial = counts["partial"]
    pending = total - verified - partial
    percent = 100 * verified / total if total else 0

    rows = []
    for index, company in enumerate(companies, start=1):
        state, label = classify_status(company)
        slug = quote(str(company["_slug"]), safe="-")
        source = quote(str(company.get("_source_path") or ""), safe="/-")
        name = company["name"]
        industry = company.get("industry") or ""
        loc = location_label(company)
        loc_status = str((company.get("location") or {}).get("status") or "")
        review = str(company.get("last_verified") or "")
        # The page exposes the original YAML for maintainers without allowing browser-side
        # toggles that could misleadingly claim permanent verification.
        source_link = (
            '<a href="https://github.com/SuhaibAtef/jordan-job-employers-index/blob/main/'
            + source + '">Source YAML</a>' if source else '—'
        )
        rows.append(
            '<tr data-status="' + esc(state) + '" data-location="' + esc(loc_status)
            + '" data-name="' + esc(name.casefold()) + '" data-search="'
            + esc((name + " " + industry).casefold()) + '" data-reviewed="' + esc(review) + '">'
            + '<td class="num">' + str(index) + '</td>'
            + '<td><a class="company" href="companies/' + slug + '.html">' + esc(name)
            + '</a><div class="industry">' + esc(industry or "Not classified") + '</div></td>'
            + '<td><span class="pill ' + state + '">' + label + '</span></td>'
            + '<td>' + esc(loc) + '</td>'
            + '<td>' + (esc(review) if review else '—') + '</td>'
            + '<td>' + source_link + '</td></tr>'
        )

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Company verification progress | Jordan Job Employers Index</title>
<style>{STYLE}</style></head><body>
<main class="wrap"><a class="back" href="index.html">← Employer directory</a>
<div class="eyebrow">Jordan Job Employers Index · Research progress</div>
<h1>Company verification progress</h1>
<p class="lead">Every company in the directory, with its recorded company-level verification status.
A verified location is not the same as a verified company record.</p>
<section class="stats" aria-label="Verification totals">
<div class="stat"><strong>{total}</strong><span>Total companies</span></div>
<div class="stat"><strong>{verified}</strong><span>Fully verified</span></div>
<div class="stat"><strong>{partial}</strong><span>Partially verified</span></div>
<div class="stat"><strong>{pending}</strong><span>Not fully reviewed / unresolved</span></div>
</section>
<div class="progress" role="progressbar" aria-label="Fully verified companies"
aria-valuemin="0" aria-valuemax="100" aria-valuenow="{percent:.1f}">
<div style="width:{percent:.1f}%"></div></div>
<p class="progress-text">{verified} of {total} companies fully verified ({percent:.1f}%).</p>
<section class="controls" aria-label="Filter companies">
<label>Search companies<input id="search" type="search" placeholder="Name or industry"></label>
<label>Company verification<select id="status">
<option value="">All statuses</option><option value="verified">Verified</option>
<option value="partial">Partially verified</option><option value="not_verified">Not verified</option>
<option value="unresolved">Unresolved</option></select></label>
<label>Location status<select id="location">
<option value="">All location statuses</option><option value="verified">Verified location</option>
<option value="provided_unverified">Provided, unverified</option>
<option value="approximate">Approximate</option><option value="unresolved">Unresolved</option>
</select></label>
<label>Sort by<select id="sort"><option value="name">Company name</option>
<option value="status">Needs verification first</option>
<option value="reviewed">Last review (newest)</option></select></label>
</section>
<div class="summary"><h2>All companies</h2><span id="visibleCount" aria-live="polite">{total} of {total} employers</span></div>
<div class="scroll"><table><thead><tr>
<th scope="col">#</th><th scope="col">Company</th><th scope="col">Company status</th>
<th scope="col">Location status</th><th scope="col">Last reviewed</th><th scope="col">Edit record</th>
</tr></thead><tbody id="companyRows">{''.join(rows)}</tbody></table></div>
<p class="note">Status comes from each YAML record's <code>verification_status</code> field.
Only <b>verified</b> counts as fully verified. <b>partial</b> is incomplete;
missing or unfamiliar values are not verified. <b>Unresolved</b> is tracked separately.
The <code>last_verified</code> field is a recorded review date, not proof of full verification.
Changes to the YAML source are reflected after the next site build.</p>
</main><script>{SCRIPT}</script></body></html>"""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "progress.html").write_text(html, encoding="utf-8")
    return counts
