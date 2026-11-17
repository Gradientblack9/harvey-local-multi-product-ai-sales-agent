"""Exercise an actual outage of the explicitly identified project-owned Ollama process."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import httpx
import psutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from local_sales import db

def start_runtime():
    env=os.environ.copy()
    env.update(OLLAMA_HOST='127.0.0.1:11434',OLLAMA_NO_CLOUD='1',OLLAMA_MODELS=str(ROOT/'models'/'ollama'),OLLAMA_NUM_PARALLEL='1',OLLAMA_MAX_LOADED_MODELS='1',OLLAMA_CONTEXT_LENGTH='4096',OLLAMA_FLASH_ATTENTION='1')
    with (ROOT/'.runtime'/'ollama-recovery-stdout.log').open('ab') as out,(ROOT/'.runtime'/'ollama-recovery-stderr.log').open('ab') as err:
        process=subprocess.Popen([str(ROOT/'.runtime'/'ollama.exe'),'serve'],cwd=ROOT/'.runtime',env=env,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (ROOT/'.runtime'/'ollama.pid').write_text(str(process.pid))
    return process.pid

def verify(pid):
    process=psutil.Process(pid)
    runtime=(ROOT/'.runtime').resolve()
    if not Path(process.exe()).resolve().is_relative_to(runtime) or 'serve' not in process.cmdline():
        raise RuntimeError('Refusing to stop a process not proven to be this project runtime')
    all_children=process.children(recursive=True)
    console_helper=(Path(os.environ.get('SystemRoot','C:/Windows'))/'System32'/'conhost.exe').resolve()
    children=[]
    for child in all_children:
        executable=Path(child.exe()).resolve()
        if executable.is_relative_to(runtime):children.append(child)
        elif executable!=console_helper:raise RuntimeError('Unexpected child process outside the project runtime')
    if db.rows("SELECT id FROM task_queue WHERE status='running'"):
        raise RuntimeError('Wait for the worker to become idle before the outage test')
    evidence={'started_at':db.now(),'stopped_project_pid':pid,'physical_internet_disabled':False}
    restarted=False
    try:
        process.terminate()
        process.wait(timeout=10)
        for child in children:
            if child.is_running():child.terminate()
        psutil.wait_procs(children,timeout=10)
        with httpx.Client(base_url='http://127.0.0.1:8000',trust_env=False,timeout=15) as client:
            response=client.get('/api/status');response.raise_for_status()
            evidence['status_while_down']=response.json()
            assert not response.json()['connected']
            response=client.post('/api/products/2/run',json={'workflow':'reply','reply_ids':[6]});response.raise_for_status()
            tid=response.json()['task_ids'][-1]
            for _ in range(30):
                task=db.one('SELECT * FROM task_queue WHERE id=?',(tid,))
                if task['status']=='waiting':break
                time.sleep(.5)
            assert task['status']=='waiting'
            evidence['task_while_down']=task
            evidence['browse_products_status']=client.get('/api/products').status_code
            evidence['browse_saved_results_status']=client.get('/api/products/1/workspace').status_code
            assert evidence['browse_products_status']==evidence['browse_saved_results_status']==200
            print('Real outage verified: task waiting, saved data accessible.',flush=True)
            evidence['restarted_project_pid']=start_runtime()
            restarted=True
            for _ in range(300):
                task=db.one('SELECT * FROM task_queue WHERE id=?',(tid,))
                if task['status'] in ('completed','failed','blocked','cancelled'):break
                time.sleep(1)
            evidence['task_after_restart']=task
            evidence['inference_logs']=db.rows('SELECT * FROM inference_logs WHERE task_id=?',(tid,))
            evidence['recovered']=task['status']=='completed'
            evidence['finished_at']=db.now()
            (ROOT/'output'/'outage-evidence.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf-8')
            assert evidence['recovered'],task.get('error')
            print('Real recovery verified: queued reply classification completed.',flush=True)
    finally:
        if not restarted:
            start_runtime()
        pause=ROOT/'.runtime'/'paused-tasks.json'
        if pause.exists():
            data=json.loads(pause.read_text())
            with db.connect() as conn:
                for t in data['tasks']:
                    conn.execute("UPDATE task_queue SET next_attempt=? WHERE id=? AND next_attempt=? AND status IN ('queued','waiting')",(t['next_attempt'],t['id'],data['until']))
            print('Previously pending tasks restored to their original schedule.',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--pid',type=int,required=True)
    verify(parser.parse_args().pid)
