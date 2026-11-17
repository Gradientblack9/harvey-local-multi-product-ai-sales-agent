import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from . import config

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def dump(value):
    return json.dumps(value, ensure_ascii=False)

@contextmanager
def connect():
    config.DATA.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(config.DB, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def rows(sql, params=()):
    with connect() as db:
        return [dict(row) for row in db.execute(sql, params).fetchall()]

def one(sql, params=()):
    result = rows(sql, params)
    return result[0] if result else None

def execute(sql, params=()):
    with connect() as db:
        return db.execute(sql, params).lastrowid

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, company_name TEXT NOT NULL,
 company_info TEXT NOT NULL, description TEXT NOT NULL, target_market TEXT NOT NULL,
 value_proposition TEXT NOT NULL, color TEXT NOT NULL DEFAULT 'green',
 sample INTEGER NOT NULL DEFAULT 0, revision INTEGER NOT NULL DEFAULT 1,
 profile_json TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS icps (
 product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
 output_json TEXT NOT NULL, task_id INTEGER, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS prospects (
 id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
 company TEXT NOT NULL, contact_name TEXT NOT NULL, title TEXT NOT NULL,
 industry TEXT NOT NULL, employees INTEGER NOT NULL, location TEXT NOT NULL,
 notes TEXT NOT NULL, sample INTEGER NOT NULL DEFAULT 0,
 research_json TEXT, problem_json TEXT, score_json TEXT, similarity REAL,
 created_at TEXT NOT NULL, UNIQUE(id,product_id)
);
CREATE TABLE IF NOT EXISTS signals (
 id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, prospect_id INTEGER NOT NULL,
 output_json TEXT NOT NULL, task_id INTEGER NOT NULL, updated_at TEXT NOT NULL,
 UNIQUE(product_id,prospect_id),
 FOREIGN KEY(prospect_id,product_id) REFERENCES prospects(id,product_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS emails (
 id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, prospect_id INTEGER NOT NULL,
 subject TEXT NOT NULL, body TEXT NOT NULL, task_id INTEGER NOT NULL,
 status TEXT NOT NULL DEFAULT 'draft', updated_at TEXT NOT NULL,
 UNIQUE(product_id,prospect_id),
 FOREIGN KEY(prospect_id,product_id) REFERENCES prospects(id,product_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS replies (
 id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, prospect_id INTEGER NOT NULL,
 thread TEXT NOT NULL, sample INTEGER NOT NULL DEFAULT 0, classification_json TEXT,
 task_id INTEGER, created_at TEXT NOT NULL,
 FOREIGN KEY(prospect_id,product_id) REFERENCES prospects(id,product_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS task_queue (
 id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
 workflow TEXT NOT NULL, prospect_id INTEGER, reply_id INTEGER,
 revision INTEGER NOT NULL, model TEXT NOT NULL, batch_id TEXT NOT NULL,
 dependencies_json TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'queued',
 attempts INTEGER NOT NULL DEFAULT 0, next_attempt REAL NOT NULL DEFAULT 0,
 error TEXT, result_json TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS queue_status ON task_queue(status,next_attempt);
CREATE TABLE IF NOT EXISTS inference_logs (
 id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL REFERENCES task_queue(id),
 product_id INTEGER NOT NULL, workflow TEXT NOT NULL, model TEXT NOT NULL,
 source TEXT NOT NULL CHECK(source='local'), endpoint TEXT NOT NULL,
 started_at TEXT NOT NULL, duration_ms INTEGER, prompt_tokens INTEGER,
 completion_tokens INTEGER, status TEXT NOT NULL, error TEXT
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
PRAGMA user_version=1;
"""

def init():
    with connect() as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript(SCHEMA)
        db.execute("UPDATE task_queue SET status='queued',error='Resumed after application restart' WHERE status='running'")
        db.execute("UPDATE inference_logs SET status='interrupted',error='Application stopped during inference' WHERE status='running'")
        db.execute("INSERT OR IGNORE INTO settings VALUES ('model',?)", (config.MODEL,))
    from .seed import seed
    seed()

def invalidate(db, product_id):
    """Input edits invalidate dependent outputs and cancel obsolete work atomically."""
    db.execute("UPDATE products SET revision=revision+1,profile_json=NULL WHERE id=?", (product_id,))
    db.execute("DELETE FROM icps WHERE product_id=?", (product_id,))
    db.execute("UPDATE prospects SET research_json=NULL,problem_json=NULL,score_json=NULL,similarity=NULL WHERE product_id=?", (product_id,))
    db.execute("DELETE FROM signals WHERE product_id=?", (product_id,))
    db.execute("DELETE FROM emails WHERE product_id=?", (product_id,))
    db.execute("UPDATE replies SET classification_json=NULL,task_id=NULL WHERE product_id=?", (product_id,))
    db.execute("UPDATE task_queue SET status='cancelled',error='Source inputs changed',updated_at=? WHERE product_id=? AND status IN ('queued','waiting','running')", (now(), product_id))

def model():
    setting = one("SELECT value FROM settings WHERE key='model'")
    return setting["value"] if setting else config.MODEL
