# Jordan Job Employers Index

Evidence-first directory of 500 employers relevant to job seekers in Jordan.

Each company is stored in a standalone YAML file under `companies/`. The website is generated from those YAML records; generated HTML is not committed.

## What job seekers can filter

The deployed directory supports full-text search plus filters for reported city/area, industry, location confidence, HR contact availability, careers-page availability, categories, technology stack, evidence type, early-career signals, job-post evidence, LinkedIn employee evidence, and application readiness.

## Evidence model

Evidence is retained per company and de-duplicated by reference. Types include official website, careers page, company listing, job post, LinkedIn company, LinkedIn employee, Google Maps, and other public sources. Missing evidence types are shown as missing rather than inferred.

Location status is explicit:

- `verified`: corroborated location evidence exists in the source dataset.
- `provided_unverified`: a specific location is supplied but is not independently marked verified.
- `approximate`: location is intentionally approximate.
- `unresolved`: public evidence conflicts or does not safely resolve to one exact location.

The city/area filter is therefore a reported/canonicalized area, not a claim that every pin is exact.

## CI/CD

CI requires:

- more than 100 company YAML files;
- unique company names;
- at least one evidence record for every company;
- non-redundant evidence references within each company;
- supported location-status values.

Pushes to `main` validate the data, build the static site, and deploy it with GitHub Pages.

## Local build

```bash
python -m pip install -r requirements.txt
python scripts/validate.py
python scripts/build.py
python -m http.server -d _site 8000
```
