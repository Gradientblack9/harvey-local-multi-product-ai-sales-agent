import json
from local_sales import db

def test_seed_inputs_only_and_product_isolation(client):
    a=client.get('/api/products/1/workspace').json()
    b=client.get('/api/products/2/workspace').json()
    assert len(a['prospects'])==len(b['prospects'])==12
    assert len(a['replies'])==len(b['replies'])==5
    assert a['product']['profile'] is None and a['icp'] is None
    assert all(p['research'] is None and p['score'] is None for p in a['prospects'])
    assert not set(p['id'] for p in a['prospects']) & set(p['id'] for p in b['prospects'])
    assert client.post('/api/products/1/run',json={'workflow':'research','prospect_ids':[13]}).status_code==422
    assert client.post('/api/products/1/replies',json={'prospect_id':13,'thread':'Please send details.'}).status_code==404
    assert client.post('/api/products/1/run',json={'workflow':'reply','reply_ids':[6]}).status_code==422

def test_input_update_invalidates_outputs_and_cancels_old_tasks(client):
    p=client.get('/api/products').json()[0]
    client.post('/api/products/1/run',json={'workflow':'pipeline','prospect_ids':[1],'reply_ids':[1]})
    db.execute("UPDATE products SET profile_json='{}' WHERE id=1")
    payload={k:p[k] for k in ('name','company_name','company_info','description','target_market','value_proposition','color')}
    payload['description']='Updated product description with new features.'
    result=client.put('/api/products/1',json=payload)
    assert result.status_code==200
    assert result.json()['revision']==2
    assert result.json()['profile'] is None
    assert all(t['status']=='cancelled' for t in db.rows('SELECT status FROM task_queue'))
    assert client.post('/api/products/1/tasks/1/retry').status_code==409
    assert client.get('/api/products/2/workspace').json()['product']['revision']==1

def test_api_security_and_static_assets(client):
    assert client.post('/api/products/1/run',json={'workflow':'icp'},headers={'Origin':'https://evil.example'}).status_code==403
    assert client.get('/',headers={'Host':'evil.example'}).status_code==400
    page=client.get('/')
    assert page.status_code==200 and "connect-src 'self'" in page.headers['content-security-policy']
    assert client.get('/fonts/geist.woff2').status_code==200
    assert client.get('/static/app.js').status_code==200
    assert client.put('/api/model',json={'model':'qwen3:4b-cloud'}).status_code==422
    assert client.get('/api/products/999/workspace').status_code==404

def test_duplicate_queue_clicks_do_not_duplicate_work(client):
    payload={'workflow':'pipeline','prospect_ids':[1,1],'reply_ids':[1]}
    first=client.post('/api/products/1/run',json=payload).json()
    second=client.post('/api/products/1/run',json=payload).json()
    assert first['created']==8 and second['created']==0
    assert len(db.rows('SELECT id FROM task_queue'))==8

def test_exports_escape_spreadsheet_formulas(client):
    db.execute("UPDATE prospects SET company='=1+2' WHERE id=1")
    csv=client.get('/api/products/1/export/prospects')
    assert csv.status_code==200 and "'=1+2" in csv.text
    assert client.get('/api/products/1/export/logs').json()==[]
    assert client.get('/api/products/1/export/not-real').status_code==404

def test_new_product_and_prospect_crud(client):
    p={'name':'Test product','company_name':'Test company','company_info':'A company for testing input persistence.','description':'A specific product description for testing.','target_market':'Local firms','value_proposition':'Save time','color':'blue'}
    created=client.post('/api/products',json=p)
    assert created.status_code==201
    pid=created.json()['id']
    prospect={'company':'Acme Test','contact_name':'Test Person','title':'Founder','industry':'Software','employees':25,'location':'Remote','notes':'Known local notes with product-relevant evidence.'}
    result=client.post(f'/api/products/{pid}/prospects',json=prospect)
    assert result.status_code==201 and result.json()['sample']==0
    prospect['employees']=30
    assert client.put(f'/api/products/{pid}/prospects/{result.json()["id"]}',json=prospect).status_code==200
    assert client.get(f'/api/products/{pid}/workspace').json()['prospects'][0]['employees']==30
