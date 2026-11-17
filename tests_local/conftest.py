import pytest
from local_sales import config,db

@pytest.fixture
def database(tmp_path,monkeypatch):
    monkeypatch.setattr(config,"DATA",tmp_path)
    monkeypatch.setattr(config,"DB",tmp_path/"test.db")
    db.init()
    return db

@pytest.fixture
def client(database,monkeypatch):
    import asyncio
    from fastapi.testclient import TestClient
    from local_sales.app import app
    from local_sales.workflows import Worker
    async def idle(self):
        await asyncio.Event().wait()
    monkeypatch.setattr(Worker,"run",idle)
    with TestClient(app) as c:
        yield c

@pytest.fixture
def outputs():
    # Scripted outputs exist only in tests; production has no fake-model mode.
    return {
        "business_profile":{"summary":"Software company selling practical business tools.","sells":["Access reviews"],"customers":["Software teams"],"value_propositions":["Reduce manual work"]},
        "icp":{"summary":"Growing software teams preparing security audits.","industries":["B2B SaaS"],"company_sizes":["50-500"],"decision_makers":["CTO"],"pain_points":["Manual evidence"],"disqualifiers":["No audit need"]},
        "research":{"summary":"The sample company is preparing an audit and hiring engineers.","icp_match_reason":"Its audit needs fit this product.","evidence":["Stored notes mention SOC 2."]},
        "signals":{"signals":[{"type":"hiring","confidence":.9,"evidence":"Stored notes mention 14 engineering hires."}]},
        "problem":{"statement":"The team may struggle to organise audit evidence.","supporting_evidence":"The notes describe spreadsheet access reviews."},
        "scoring":{"score":82,"priority":"high","reason":"Fits the target market and has explicit audit needs."},
        "email":{"subject":"Access reviews at Meridian","body":"Hi Avery, your audit preparation may benefit from organised access evidence. Would a brief overview help?"},
        "reply":{"category":"Interested","confidence":.95,"reason":"The contact explicitly asks to meet."},
    }
