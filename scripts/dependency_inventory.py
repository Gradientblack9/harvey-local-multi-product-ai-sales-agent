"""Record resolved runtime dependency versions and licence metadata without network access."""
from importlib.metadata import distribution,PackageNotFoundError
from pathlib import Path
from packaging.requirements import Requirement
import json

ROOT=Path(__file__).resolve().parents[1]
pending=['fastapi','uvicorn','httpx','pydantic','psutil','sentence-transformers','pytest']
seen={}
while pending:
    name=pending.pop()
    key=name.lower().replace('_','-')
    if key in seen:continue
    try:dist=distribution(name)
    except PackageNotFoundError:continue
    meta=dist.metadata
    seen[key]={'name':meta['Name'],'version':dist.version,'license_expression':meta.get('License-Expression'),'license_summary':(meta.get('License') or '')[:160],'project_urls':meta.get_all('Project-URL') or [],'license_files':meta.get_all('License-File') or []}
    for value in dist.requires or []:
        req=Requirement(value)
        if req.marker is None or req.marker.evaluate({'extra':''}):pending.append(req.name)
result={'purpose':'Resolved versions and installed metadata from this verification environment. This is a platform-specific snapshot; direct dependencies are pinned in pyproject.toml.','packages':sorted(seen.values(),key=lambda p:p['name'].lower())}
(ROOT/'docs'/'local-dependency-inventory.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(ROOT/'requirements-verified.txt').write_text('# Windows Python 3.13 dependency snapshot from this build.\n'+'\n'.join(f"{p['name']}=={p['version']}" for p in result['packages'])+'\n',encoding='utf-8')
print(f"Recorded {len(seen)} installed dependency versions and licence metadata.")
