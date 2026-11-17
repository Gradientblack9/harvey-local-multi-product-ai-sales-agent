import asyncio
import httpx
import pytest
from local_sales import db
from local_sales.llm_client import LocalLLM,InvalidOutput,ModelUnavailable,validate_model
from local_sales.schemas import BusinessProfile,SCHEMAS,RunInput
from local_sales.workflows import enqueue,Worker
from local_sales.hardware import recommend

def make_task():
    enqueue(1,RunInput(workflow='business_profile'))
    return db.one('SELECT * FROM task_queue LIMIT 1')

def test_bad_json_retried_and_every_attempt_logged(database,outputs):
    calls=[]
    def handler(request):
        assert request.url.host=='127.0.0.1' and request.url.port==11434
        calls.append(request)
        return httpx.Response(200,json={'message':{'content':'not json' if len(calls)==1 else db.dump(outputs['business_profile'])},'prompt_eval_count':23,'eval_count':45})
    async def run():
        llm=LocalLLM(httpx.MockTransport(handler))
        result=await llm.generate(make_task(),BusinessProfile,'Summarise the business',{})
        await llm.close()
        return result
    assert asyncio.run(run())==outputs['business_profile']
    logs=db.rows('SELECT * FROM inference_logs ORDER BY id')
    assert [l['status'] for l in logs]==['invalid_json','success']
    assert all(l['source']=='local' and l['prompt_tokens']==23 and l['completion_tokens']==45 for l in logs)

def test_invalid_json_stops_after_three_attempts(database):
    async def run():
        llm=LocalLLM(httpx.MockTransport(lambda r:httpx.Response(200,json={'message':{'content':'{}'}})))
        try:
            with pytest.raises(InvalidOutput):
                await llm.generate(make_task(),BusinessProfile,'test',{})
        finally:
            await llm.close()
    asyncio.run(run())
    assert len(db.rows('SELECT id FROM inference_logs'))==3

def test_mid_request_runtime_disconnect_is_recoverable(database):
    def handler(request):raise httpx.RemoteProtocolError('Local runtime stopped')
    async def run():
        llm=LocalLLM(httpx.MockTransport(handler))
        try:
            with pytest.raises(ModelUnavailable):await llm.generate(make_task(),BusinessProfile,'test',{})
        finally:await llm.close()
    asyncio.run(run())
    assert db.one('SELECT status FROM inference_logs')['status']=='unavailable'

def test_redirect_never_followed(database):
    seen=[]
    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(302,headers={'Location':'https://example.test/inference'})
    async def run():
        llm=LocalLLM(httpx.MockTransport(handler))
        try:
            with pytest.raises(InvalidOutput):
                await llm.generate(make_task(),BusinessProfile,'test',{})
        finally:
            await llm.close()
    asyncio.run(run())
    assert seen==['http://127.0.0.1:11434/api/chat']

def test_unavailable_model_waits_then_resumes_all_eight_workflows(database,outputs):
    class FakeLLM:
        ready=False
        calls=[]
        async def health(self,model):return {'connected':self.ready,'message':'Local model offline'}
        async def generate(self,task,schema,instruction,context):
            self.calls.append(task['workflow'])
            assert context['product']['id']==1
            return schema.model_validate(outputs[task['workflow']]).model_dump()
    class FakeEmbeddings:
        def similarity(self,a,b):return .6
    async def run():
        llm=FakeLLM()
        worker=Worker(llm)
        worker.embeddings=FakeEmbeddings()
        enqueue(1,RunInput(workflow='pipeline',prospect_ids=[1],reply_ids=[1]))
        await worker.tick()
        assert db.one('SELECT status FROM task_queue WHERE id=1')['status']=='waiting'
        assert llm.calls==[]
        assert db.rows('SELECT * FROM inference_logs')==[]
        llm.ready=True
        db.execute('UPDATE task_queue SET next_attempt=0')
        for _ in range(8):await worker.tick()
        assert set(llm.calls)==set(SCHEMAS)
        assert all(t['status']=='completed' for t in db.rows('SELECT status FROM task_queue'))
        assert db.one('SELECT count(*) n FROM emails WHERE product_id=1')['n']==1
        assert db.one('SELECT count(*) n FROM emails WHERE product_id=2')['n']==0
        assert db.one('SELECT similarity FROM prospects WHERE id=1')['similarity']==.6
    asyncio.run(run())

def test_input_revision_discards_inflight_result(database,outputs):
    task=make_task()
    db.execute("UPDATE task_queue SET status='running' WHERE id=?",(task['id'],))
    with db.connect() as conn:db.invalidate(conn,1)
    Worker(None).persist(task,outputs['business_profile'],{})
    assert db.one('SELECT profile_json FROM products WHERE id=1')['profile_json'] is None
    assert db.one('SELECT status FROM task_queue WHERE id=1')['status']=='cancelled'

def test_failed_dependency_blocks_descendants(database):
    enqueue(1,RunInput(workflow='icp'))
    db.execute("UPDATE task_queue SET status='failed' WHERE workflow='business_profile'")
    asyncio.run(Worker(None).tick())
    assert db.one("SELECT status FROM task_queue WHERE workflow='icp'")['status']=='blocked'

def test_hardware_model_safety():
    assert recommend(6)[0]=='qwen3:1.7b'
    assert recommend(16)[0]=='qwen3:4b'
    assert recommend(32)[0]=='qwen3:8b'
    assert recommend(16,12)[0]=='qwen3:8b'
    with pytest.raises(ValueError):validate_model('unknown:cloud')

def test_schema_rejects_invalid_scores_and_confidence():
    with pytest.raises(ValueError):SCHEMAS['scoring'].model_validate({'score':120,'priority':'high','reason':'A long enough explanation.'})
    with pytest.raises(ValueError):SCHEMAS['reply'].model_validate({'category':'Interested','confidence':1.5,'reason':'Requested a meeting.'})
