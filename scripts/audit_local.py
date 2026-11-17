"""Audit the executable local package and explicitly report retained legacy matches."""
import ast
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
PRD_TERMS=['open'+'ai','anthro'+'pic','api'+'_'+'key','gemi'+'ni']
PATTERN=re.compile('|'.join(PRD_TERMS+['clau'+'de','co'+'dex']),re.I)
active=[]
imports=set()
for path in (ROOT/'local_sales').rglob('*'):
    if path.suffix not in ('.py','.js','.html','.css'):
        continue
    text=path.read_text(encoding='utf-8')
    for i,line in enumerate(text.splitlines(),1):
        if PATTERN.search(line):active.append({'file':str(path.relative_to(ROOT)),'line':i,'text':line[:180]})
    if path.suffix=='.py':
        for node in ast.walk(ast.parse(text)):
            if isinstance(node,ast.Import):imports.update(n.name.split('.')[0] for n in node.names)
            if isinstance(node,ast.ImportFrom) and node.module:imports.add(node.module.split('.')[0])
legacy=[]
for name in ('harvey','prompts','skills','tests'):
    for path in (ROOT/name).rglob('*'):
        if path.suffix in ('.py','.js','.html','.md','.yaml') and '__pycache__' not in path.parts:
            text=path.read_text(encoding='utf-8',errors='replace')
            count=len(PATTERN.findall(text))
            if count:legacy.append({'file':str(path.relative_to(ROOT)),'matches':count})
for name in ('.env.example','CLAUDE.md','CHANGELOG.md','harvey.yaml'):
    path=ROOT/name
    if path.exists():
        count=len(PATTERN.findall(path.read_text(encoding='utf-8',errors='replace')))
        if count:legacy.append({'file':name,'matches':count})
repository_matches=[]
skip={'.git','.venv','.runtime','models','data','output','__pycache__','.pytest_cache'}
required_pattern=re.compile('|'.join(PRD_TERMS),re.I)
for path in ROOT.rglob('*'):
    if any(part in skip for part in path.relative_to(ROOT).parts) or path.suffix not in ('.py','.js','.html','.css','.md','.txt','.toml','.ini','.yaml','.yml','.json'):
        continue
    for number,line in enumerate(path.read_text(encoding='utf-8',errors='replace').splitlines(),1):
        if required_pattern.search(line):repository_matches.append({'file':str(path.relative_to(ROOT)),'line':number,'text':line[:180]})
result={'runtime_package':'local_sales','runtime_pass':not active,'runtime_matches':active,'runtime_imports':sorted(imports),'whole_repository_pass':not repository_matches and not legacy,'repository_matches':repository_matches,'retained_legacy_matches':legacy,'note':'Scans code, tests, docs, scripts and manifests. Excludes Git history, downloaded environments/models, user data, generated evidence and caches.'}
target=ROOT/'output'/'runtime-audit.json'
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'runtime_pass':result['runtime_pass'],'runtime_matches':len(active),'legacy_files_with_matches':len(legacy),'repository_matches':len(repository_matches),'whole_repository_pass':result['whole_repository_pass']},indent=2))
sys.exit(0 if result['runtime_pass'] and result['whole_repository_pass'] else 1)
