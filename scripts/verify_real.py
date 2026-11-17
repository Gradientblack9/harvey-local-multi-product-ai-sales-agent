"""Capture actual local-model evidence and compare product ICPs under a socket guard.

This is process-level egress denial, not a claim that physical Wi-Fi was disabled.
Run from the project root after the first pipeline has finished.
"""
import asyncio
import json
from pathlib import Path
import socket
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from local_sales import db
from local_sales.llm_client import LocalLLM
from local_sales.schemas import SCHEMAS
from local_sales.workflows import Worker,INSTRUCTIONS

blocked=[]
allowed={'127.0.0.1','::1','localhost'}
original_connect=socket.socket.connect
original_connect_ex=socket.socket.connect_ex
original_dns=socket.getaddrinfo
def guarded_connect(self,address):
    if isinstance(address,tuple) and address[0] not in allowed:
        blocked.append(str(address))
        raise OSError('Verification guard blocked non-loopback connection')
    return original_connect(self,address)
def guarded_connect_ex(self,address):
    if isinstance(address,tuple) and address[0] not in allowed:
        blocked.append(str(address))
        raise OSError('Verification guard blocked non-loopback connection')
    return original_connect_ex(self,address)
def guarded_dns(host,*args,**kwargs):
    name=host.decode() if isinstance(host,bytes) else host
    if name is not None and name not in allowed:
        blocked.append(str(name))
        raise OSError('Verification guard blocked external DNS')
    return original_dns(host,*args,**kwargs)

async def verify():
    prior=db.rows("SELECT DISTINCT workflow FROM task_queue WHERE product_id=1 AND status='completed'")
    completed={r['workflow'] for r in prior}
    if not set(SCHEMAS)<=completed:
        raise RuntimeError('Wait until one real run of all eight workflows completes before capturing evidence.')
    socket.socket.connect=guarded_connect
    socket.socket.connect_ex=guarded_connect_ex
    socket.getaddrinfo=guarded_dns
    try:
        with socket.socket() as probe:
            try:probe.connect(('203.0.113.1',443))
            except OSError:pass
        llm=LocalLLM()
        worker=Worker(llm)
        try:
            for workflow in ('business_profile','icp'):
                product=db.one('SELECT * FROM products WHERE id=2')
                tid=db.execute("INSERT INTO task_queue(product_id,workflow,revision,model,batch_id,status,attempts,created_at,updated_at) VALUES (2,?,?,?,?, 'running',1,?,?)",(workflow,product['revision'],db.model(),'guard-'+uuid.uuid4().hex[:8],db.now(),db.now()))
                task=db.one('SELECT * FROM task_queue WHERE id=?',(tid,))
                try:
                    context=await worker.context(task)
                    result=await llm.generate(task,SCHEMAS[workflow],INSTRUCTIONS[workflow],context)
                    worker.persist(task,result,context)
                    print(f'Guarded real inference complete: product 2 / {workflow}',flush=True)
                except Exception as exc:
                    db.execute("UPDATE task_queue SET status='failed',error=?,updated_at=? WHERE id=?",(str(exc),db.now(),tid))
                    raise
        finally:
            await llm.close()
    finally:
        socket.socket.connect=original_connect
        socket.socket.connect_ex=original_connect_ex
        socket.getaddrinfo=original_dns
    icps=db.rows('SELECT * FROM icps WHERE product_id IN (1,2) ORDER BY product_id')
    assert len(icps)==2 and icps[0]['output_json']!=icps[1]['output_json']
    logs=db.rows('SELECT * FROM inference_logs ORDER BY id')
    evidence={'captured_at':db.now(),'method':'Real Ollama inference; process-level non-loopback socket/DNS guard for product 2 comparison. Physical Wi-Fi remained enabled.','all_eight_workflows_completed':sorted(completed),'different_product_icps':True,'blocked_probe':blocked,'logs':logs,'icps':[{**i,'output':json.loads(i['output_json'])} for i in icps],'tasks':db.rows("SELECT * FROM task_queue WHERE status='completed' ORDER BY id")}
    target=ROOT/'output'/'real-inference-evidence.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Real evidence captured in output/real-inference-evidence.json',flush=True)

if __name__=='__main__':asyncio.run(verify())
