# Jordan Job Employers Index

Evidence-first directory of 500 employers relevant to job seekers in Jordan.

Each company is stored in a standalone YAML file under `companies/`. The website is generated from those YAML records; generated HTML is not committed.

## What job seekers can filter

The deployed directory supports full-text search plus filters for reported city/area, industry, location confidence, HR contact availability, careers-page availability, categories, technology stack, evidence type, early-career signals, job-post evidence, LinkedIn employee evidence, and application readiness.

## Application tracker export

On the directory page, apply any search and filters, then select **Download application tracker (.csv)**. The downloaded UTF-8 CSV contains the companies currently shown (in their displayed order), with company name, website, careers URL, public HR email, available research details, and editable columns for application status, job title, dates, private notes, and follow-up actions.

Import the CSV into **Google Sheets** (File → Import → Upload) or open it in Excel. The first 16 columns are based on the [Jordan companies tracking-sheet example](https://docs.google.com/spreadsheets/d/14U8Gzwci0PlQf1C23uY9nXJnuK1x4e-VP_mtkKZ5z3Q/edit). Fields not supported by the source company records, such as HR LinkedIn contacts, worldwide/Jordan employee estimates and business-model classifications, are deliberately left blank rather than guessed. The company size reported in the directory is available in a separate column.

This is a client-side download: it does not upload, store, or sync student application information. Each export is a fresh snapshot, so keep editing your own imported tracker instead of re-importing whenever you return to the directory.

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
