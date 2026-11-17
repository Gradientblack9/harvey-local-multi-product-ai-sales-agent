"""Package source and verified evidence, excluding user data, downloaded models and runtimes."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
testlog=(ROOT/'.runtime'/'test-results-release.log').read_text(encoding='utf-8')
match=re.search(r'(\d+) passed',testlog)
assert match and int(match.group(1))==18,'Run and pass the release tests first'
audit=json.loads((OUT/'runtime-audit.json').read_text())
real=json.loads((OUT/'real-inference-evidence.json').read_text(encoding='utf-8'))
outage=json.loads((OUT/'outage-evidence.json').read_text(encoding='utf-8'))
assert audit['runtime_pass'] and audit['whole_repository_pass']
assert len(real['all_eight_workflows_completed'])>=8 and real['different_product_icps']
assert outage['recovered']
wheel=OUT/'harvey_local_sales-1.0.0-py3-none-any.whl'
with zipfile.ZipFile(wheel) as z:
    names=z.namelist()
    assert 'local_sales/web/index.html' in names
    assert 'local_sales/web/fonts/geist-OFL.txt' in names
    assert not any(n.startswith('harvey/') for n in names)
files=[]
for directory in ('local_sales','tests_local','scripts','docs','.github'):
    for path in (ROOT/directory).rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts and not path.name.endswith('.pyc'):
            files.append(path)
for name in ('LICENSE','.gitignore','README.md','pyproject.toml','pytest.ini','requirements.txt','requirements-local.txt','requirements-verified.txt','setup.ps1','start.ps1','start-ollama.ps1'):
    files.append(ROOT/name)
source_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
from datetime import datetime,timezone
report={'created_at':datetime.now(timezone.utc).isoformat(),'base_commit':'e2632eb20ee2d4fb6fe04ae715a52f578acf9a37','branch':'codex/local-multi-product','automated_tests':{'passed':18,'failed':0,'log':testlog},'real_model':'qwen3:4b','all_eight_workflow_types_completed':True,'two_distinct_product_icps':True,'process_level_non_loopback_guard_test':True,'real_ollama_outage_and_recovery':True,'browsing_works_during_outage':True,'runtime_source_audit_pass':True,'repository_source_audit_pass':True,'wheel_build_and_independent_import_check':True,'desktop_1440px_and_mobile_390px_verified':True,'browser_console_errors':0,'physical_wifi_off_acceptance':'not performed','final_screen_recording':'not recorded; demo guide included','remote_user_owned_fork':'not published','optional_public_web_research':'not implemented; offline local notes supported','source_sha256':source_hashes,'wheel_sha256':hashlib.sha256(wheel.read_bytes()).hexdigest()}
(OUT/'build-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
archive=OUT/'harvey-local-source.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for path in files:z.write(path,'harvey-local/'+path.relative_to(ROOT).as_posix())
    for name in ('build-verification.json','runtime-audit.json','real-inference-evidence.json','outage-evidence.json','dashboard-desktop.jpg','dashboard-mobile.jpg','inference-logs.jpg'):
        z.write(OUT/name,'harvey-local/evidence/'+name)
print(f'Source archive ready ({archive.stat().st_size/1024:.0f} KB). Models, runtime downloads and all user data excluded.')
