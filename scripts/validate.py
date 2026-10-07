from pathlib import Path
import sys, yaml

ROOT = Path(__file__).resolve().parents[1]
files = sorted((ROOT / "companies").glob("*.yml"))
errors = []

if len(files) <= 100:
    errors.append(f"company_count must be > 100; got {len(files)}")

names = set()
allowed = {"verified", "provided_unverified", "approximate", "unresolved"}

for path in files:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path}: invalid YAML: {exc}")
        continue
    name = data.get("name")
    if not name:
        errors.append(f"{path}: missing name")
    elif name in names:
        errors.append(f"{path}: duplicate company name {name!r}")
    else:
        names.add(name)

    if data.get("last_verified") and not str(data.get("description") or "").strip():
        errors.append(f"{path}: verified company must include description")

    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{path}: evidence must be a non-empty list")
    else:
        refs=set()
        for i, item in enumerate(evidence):
            if not isinstance(item, dict) or not item.get("type"):
                errors.append(f"{path}: evidence[{i}] missing type")
                continue
            ref=item.get("url") or item.get("reference")
            if not ref:
                errors.append(f"{path}: evidence[{i}] missing url/reference")
                continue
            norm=str(ref).rstrip("/").lower()
            if norm in refs:
                errors.append(f"{path}: duplicate evidence reference {ref}")
            refs.add(norm)

    status=(data.get("location") or {}).get("status")
    if status not in allowed:
        errors.append(f"{path}: unsupported location.status {status!r}")

if errors:
    print("\n".join(errors))
    sys.exit(1)

print(f"OK: {len(files)} company files; every company has evidence.")
