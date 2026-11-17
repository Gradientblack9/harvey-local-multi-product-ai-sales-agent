import asyncio
import csv
import io
import json
import time
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from . import config, db, hardware
from .schemas import ProductInput, ProspectInput, ReplyInput, RunInput, ModelInput
from .llm_client import LocalLLM
from .workflows import Worker, enqueue

@asynccontextmanager
async def lifespan(app):
    db.init()
    app.state.llm = LocalLLM()
    app.state.worker = Worker(app.state.llm)
    app.state.hardware = await asyncio.to_thread(hardware.inspect)
    worker = asyncio.create_task(app.state.worker.run())
    yield
    app.state.worker.stopping = True
    worker.cancel()
    try:
        await worker
    except asyncio.CancelledError:
        pass
    await app.state.llm.close()

app = FastAPI(title="Harvey Local Sales",version="1.0.0",lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url="/api/openapi.json")
app.add_middleware(TrustedHostMiddleware,allowed_hosts=["127.0.0.1","localhost","testserver"])
WEB = Path(__file__).parent / "web"
app.mount("/static",StaticFiles(directory=WEB),name="static")
app.mount("/fonts",StaticFiles(directory=WEB / "fonts"),name="fonts")

@app.middleware("http")
async def local_headers(request:Request,call_next):
    origin = request.headers.get("origin")
    if request.method not in ("GET","HEAD","OPTIONS") and origin:
        from urllib.parse import urlparse
        parsed = urlparse(origin)
        if parsed.scheme != "http" or parsed.netloc != request.headers.get("host"):
            return JSONResponse({"detail":"Cross-origin writes are not allowed"},status_code=403)
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response

def product_or_404(pid):
    product = db.one("SELECT * FROM products WHERE id=?",(pid,))
    if product is None:
        raise HTTPException(404,"Product not found")
    return product

def record_or_404(table,rid,pid):
    record = db.one(f"SELECT * FROM {table} WHERE id=? AND product_id=?",(rid,pid))
    if record is None:
        raise HTTPException(404,"Record not found in selected product")
    return record

def unpack(row):
    row = dict(row)
    for key in list(row):
        if key.endswith("_json"):
            value = row.pop(key)
            row[key[:-5]] = json.loads(value) if value else None
    return row

@app.get("/")
def index():
    return FileResponse(WEB / "index.html")

@app.get("/api/docs",include_in_schema=False)
def api_docs():
    return HTMLResponse('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Harvey Local API</title><link rel="stylesheet" href="/static/app.css"><main><h1>Harvey Local API</h1><p class="settings-intro spaced">The complete API schema is available locally, with no external documentation assets.</p><p><a class="button" href="/api/openapi.json">Open JSON schema</a> <a class="button" href="/">Return to workspace</a></p><pre class="code">GET /api/status\nGET /api/products\nGET /api/products/{id}/workspace\nPOST /api/products/{id}/run\nGET /api/products/{id}/logs</pre><p class="spaced">Example run body:</p><pre class="code">{"workflow":"pipeline","prospect_ids":[1],"reply_ids":[1]}</pre></main></html>')

@app.get("/api/status")
async def status(request:Request):
    health = await request.app.state.llm.health()
    return {**health,"source":"local","hardware":request.app.state.hardware,"embeddings_ready":(config.EMBEDDING_PATH/"modules.json").is_file(),"endpoint":config.OLLAMA_URL,"version":"1.0.0"}

@app.put("/api/model")
def model(body:ModelInput):
    db.execute("UPDATE settings SET value=? WHERE key='model'",(body.model,))
    return {"model":body.model,"message":"New tasks use this model. Existing tasks retain their recorded model."}

@app.get("/api/products")
def products():
    return [unpack(r) for r in db.rows("SELECT * FROM products ORDER BY id")]

@app.post("/api/products",status_code=201)
def create_product(body:ProductInput):
    fields = list(body.model_dump())
    pid = db.execute(f"INSERT INTO products({','.join(fields)},created_at) VALUES ({','.join('?' for _ in range(len(fields)+1))})",(*body.model_dump().values(),db.now()))
    return unpack(product_or_404(pid))

@app.put("/api/products/{pid}")
def edit_product(pid:int,body:ProductInput):
    product_or_404(pid)
    with db.connect() as conn:
        conn.execute(f"UPDATE products SET {','.join(k+'=?' for k in body.model_dump())} WHERE id=?",(*body.model_dump().values(),pid))
        db.invalidate(conn,pid)
    return unpack(product_or_404(pid))

@app.get("/api/products/{pid}/workspace")
def workspace(pid:int):
    product = product_or_404(pid)
    icp = db.one("SELECT * FROM icps WHERE product_id=?",(pid,))
    prospects = [unpack(r) for r in db.rows("SELECT p.*,s.output_json AS signals_json,e.subject,e.body,e.task_id AS email_task_id FROM prospects p LEFT JOIN signals s ON s.product_id=p.product_id AND s.prospect_id=p.id LEFT JOIN emails e ON e.product_id=p.product_id AND e.prospect_id=p.id WHERE p.product_id=? ORDER BY COALESCE(json_extract(p.score_json,'$.score'),-1) DESC,p.company",(pid,))]
    replies = [unpack(r) for r in db.rows("SELECT r.*,p.company,p.contact_name FROM replies r JOIN prospects p ON p.id=r.prospect_id AND p.product_id=r.product_id WHERE r.product_id=? ORDER BY r.id",(pid,))]
    tasks = [unpack(r) for r in db.rows("SELECT t.*,p.company FROM task_queue t LEFT JOIN prospects p ON p.id=t.prospect_id AND p.product_id=t.product_id WHERE t.product_id=? ORDER BY t.id DESC LIMIT 500",(pid,))]
    counts = {r["status"]:r["n"] for r in db.rows("SELECT status,count(*) n FROM task_queue WHERE product_id=? GROUP BY status",(pid,))}
    return {"product":unpack(product),"icp":json.loads(icp["output_json"]) if icp else None,"prospects":prospects,"replies":replies,"tasks":tasks,"counts":counts,
        "stats":{"prospects":len(prospects),"qualified":sum(1 for p in prospects if (p.get("score") or {}).get("score",0)>=70),"drafts":sum(1 for p in prospects if p["subject"]),"classified":sum(1 for r in replies if r["classification"])}}

@app.post("/api/products/{pid}/prospects",status_code=201)
def create_prospect(pid:int,body:ProspectInput):
    product_or_404(pid)
    fields = list(body.model_dump())
    rid = db.execute(f"INSERT INTO prospects(product_id,{','.join(fields)},created_at) VALUES ({','.join('?' for _ in range(len(fields)+2))})",(pid,*body.model_dump().values(),db.now()))
    return unpack(record_or_404("prospects",rid,pid))

@app.put("/api/products/{pid}/prospects/{rid}")
def edit_prospect(pid:int,rid:int,body:ProspectInput):
    record_or_404("prospects",rid,pid)
    with db.connect() as conn:
        conn.execute(f"UPDATE prospects SET {','.join(k+'=?' for k in body.model_dump())} WHERE id=? AND product_id=?",(*body.model_dump().values(),rid,pid))
        db.invalidate(conn,pid)
    return unpack(record_or_404("prospects",rid,pid))

@app.post("/api/products/{pid}/replies",status_code=201)
def create_reply(pid:int,body:ReplyInput):
    record_or_404("prospects",body.prospect_id,pid)
    rid = db.execute("INSERT INTO replies(product_id,prospect_id,thread,created_at) VALUES (?,?,?,?)",(pid,body.prospect_id,body.thread,db.now()))
    return unpack(record_or_404("replies",rid,pid))

@app.post("/api/products/{pid}/run",status_code=202)
def run(pid:int,body:RunInput):
    product_or_404(pid)
    try:
        return enqueue(pid,body)
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc

@app.post("/api/products/{pid}/tasks/{tid}/retry")
def retry(pid:int,tid:int):
    product = product_or_404(pid)
    task = record_or_404("task_queue",tid,pid)
    if task["revision"] != product["revision"]:
        raise HTTPException(409,"Inputs changed. Start a new workflow from the dashboard.")
    if task["status"] not in ("failed","blocked","waiting"):
        raise HTTPException(409,"This task cannot be retried in its current state")
    with db.connect() as conn:
        conn.execute("UPDATE task_queue SET status='queued',next_attempt=0,error=NULL,updated_at=? WHERE id=?",(db.now(),tid))
        # Descendants blocked by this failure can be reconsidered safely by the worker.
        conn.execute("UPDATE task_queue SET status='queued',next_attempt=0,error=NULL,updated_at=? WHERE product_id=? AND revision=? AND status='blocked'",(db.now(),pid,product["revision"]))
    return {"message":"Task queued for retry"}

@app.post("/api/products/{pid}/tasks/cancel")
def cancel(pid:int):
    product_or_404(pid)
    db.execute("UPDATE task_queue SET status='cancelled',error='Cancelled by user',updated_at=? WHERE product_id=? AND status IN ('queued','waiting','running')",(db.now(),pid))
    return {"message":"Pending tasks cancelled. An in-flight model call may finish; its result will be discarded."}

@app.get("/api/products/{pid}/logs")
def logs(pid:int,limit:int=100):
    product_or_404(pid)
    return db.rows("SELECT * FROM inference_logs WHERE product_id=? ORDER BY id DESC LIMIT ?",(pid,max(1,min(limit,1000))))

@app.get("/api/products/{pid}/export/{kind}")
def export(pid:int,kind:str):
    product_or_404(pid)
    if kind == "logs":
        content = db.dump(db.rows("SELECT * FROM inference_logs WHERE product_id=? ORDER BY id",(pid,)))
        return Response(content,media_type="application/json",headers={"Content-Disposition":f'attachment; filename="product-{pid}-inference-logs.json"'})
    if kind == "workspace":
        return Response(db.dump(workspace(pid)),media_type="application/json",headers={"Content-Disposition":f'attachment; filename="product-{pid}-workspace.json"'})
    if kind != "prospects":
        raise HTTPException(404,"Unknown export")
    prospects = workspace(pid)["prospects"]
    out = io.StringIO(newline="")
    fields = ["company","contact_name","title","industry","employees","location","score","reason","subject","body","sample"]
    writer = csv.DictWriter(out,fieldnames=fields)
    writer.writeheader()
    for p in prospects:
        row = {k:p.get(k,"") for k in fields}
        row["score"] = (p["score"] or {}).get("score","")
        row["reason"] = (p["score"] or {}).get("reason","")
        # Prevent spreadsheet formula execution when opening user-entered text.
        writer.writerow({k:("'"+v if isinstance(v,str) and v.lstrip().startswith(("=","+","-","@")) else v) for k,v in row.items()})
    return Response(out.getvalue(),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="product-{pid}-prospects.csv"'})
