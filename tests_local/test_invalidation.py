import asyncio
from local_sales import db,config
from local_sales.embeddings import LocalEmbeddings,EmbeddingsUnavailable
from local_sales.workflows import clear_descendants
import pytest

def test_new_icp_clears_only_its_product_descendants(database):
    db.execute("UPDATE prospects SET research_json='{}',problem_json='{}',score_json='{}',similarity=.5")
    with db.connect() as conn:clear_descendants(conn,'icp',1,None)
    assert all(p['research_json'] is None and p['score_json'] is None and p['similarity'] is None for p in db.rows('SELECT * FROM prospects WHERE product_id=1'))
    assert all(p['research_json']=='{}' and p['score_json']=='{}' for p in db.rows('SELECT * FROM prospects WHERE product_id=2'))

def test_embedding_model_missing_fails_without_download(database,tmp_path,monkeypatch):
    monkeypatch.setattr(config,'EMBEDDING_PATH',tmp_path/'absent-model')
    with pytest.raises(EmbeddingsUnavailable,match='missing'):
        LocalEmbeddings().similarity('a','b')

def test_restart_recovers_interrupted_queue_and_log(database):
    from local_sales.workflows import enqueue
    from local_sales.schemas import RunInput
    enqueue(1,RunInput(workflow='business_profile'))
    db.execute("UPDATE task_queue SET status='running'")
    db.execute("INSERT INTO inference_logs(task_id,product_id,workflow,model,source,endpoint,started_at,status) VALUES (1,1,'business_profile','qwen3:4b','local','http://127.0.0.1:11434/api/chat',?,'running')",(db.now(),))
    db.init()
    assert db.one('SELECT status FROM task_queue')['status']=='queued'
    assert db.one('SELECT status FROM inference_logs')['status']=='interrupted'
