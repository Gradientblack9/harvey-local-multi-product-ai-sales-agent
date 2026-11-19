# Harvey Local Sales

A private, multi-product sales workspace powered by Ollama on your own machine.
FastAPI, SQLite, local Sentence Transformers embeddings, and a dashboard with bundled fonts and assets.

The dashboard uses a plain black-and-white layout with Times New Roman. Branding is a simple text heading, with no logo, sidebar promotional message or page footer.

## EDXSO Assignment 2 submission

**[One-page submission PDF](docs/submission-one-page.pdf)** | [Technical report](docs/submission-report.md) | [Video demonstration](https://drive.google.com/file/d/1yE9wX_hgOdah1AvPohjAdwIcLFRORUrx/view?usp=sharing)

**Repository:** https://github.com/Gradientblack9/harvey-local-multi-product-ai-sales-agent

This is a genuine fork of Harvey, based on the MIT-licensed v0.3.0 revision. The default `assignment-2` branch contains the local implementation. The upstream project's current default branch uses a different licence; this implementation preserves its pinned MIT base and attribution.

This submission is **locally runnable**. No public deployment is provided. AI generation runs on the user's computer through Ollama, and there is no cloud inference fallback.

See the [assignment requirements and deliverables](docs/assignment-submission.md), [technical architecture](docs/local-architecture.md), [cost/licence statement](docs/local-licenses.md), and [test evidence](evidence/README.md).

**Demo supplied:** the submitter confirms that the linked recording includes the disconnected test. Video access, duration, complete workflow coverage and exact recorded commit have not been independently verified. The earlier process-level network guard remains separate historical evidence; see [current submission status](evidence/submission-status.json).

## Run on Windows

Requires Python 3.11+ and at least 12 GB free disk space for the portable runtime, language model, embeddings and Python dependencies. A 16 GB laptop can run the default 4B model; CPU calls may take several minutes. Start with one prospect.

```powershell
git clone https://github.com/Gradientblack9/harvey-local-multi-product-ai-sales-agent.git
cd harvey-local-multi-product-ai-sales-agent
.\setup.ps1
.\start.ps1
```

If PowerShell blocks local scripts, use a one-process policy override:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Open **http://127.0.0.1:8000**. Setup requires internet to install dependencies and download models. Once those files are local, all eight workflows run without it. There is no hosted deployment.

After setup, Windows users can also double-click **`Start Harvey.cmd`** in the project folder. Keep its console window open while using the dashboard. If the browser says `ERR_CONNECTION_REFUSED`, the dashboard is stopped: start the launcher first, then refresh the browser. A browser tab alone does not start the application.

Setup defaults to `qwen3:4b`. For a smaller or larger model:

```powershell
.\setup.ps1 -Model qwen3:1.7b
```

On subsequent launches only `start.ps1` is needed. Use Ctrl+C to stop the dashboard. The portable Ollama service remains available until stopped; its PID, when started by the script, is stored in `.runtime/ollama.pid`. Closing the dashboard does not delete data. Do not run multiple dashboard workers against one database.

## First run

1. Select **Sentinel** (access governance) or **Relay** (support operations).
2. Open the product settings to inspect or edit company and product information.
3. Click **Run pipeline** and choose one prospect for an initial CPU run.
4. Watch **Task queue**. Dependencies run in order; prerequisites are added automatically.
5. Inspect the prospect's research, signals, problem, score and draft. Replies and logs have dedicated pages.
6. Switch products. All inputs, outputs, queue records and inference logs are product scoped.

The two sample products, 24 sample prospect records and 10 reply threads are **fictional inputs**. No generated profile, ICP, research, score, draft or classification is seeded. All production AI output comes from the local model. No email sending is implemented.

Individual workflows are available on Overview. Prospects supports search, selection, adding/editing source records and CSV export. Product information, records and generated results are editable or reviewable from the UI; editing source inputs invalidates dependent AI results to avoid stale outreach. Logs and workspaces can be exported as JSON through the API.

## Eight workflows

| Workflow | Output |
| --- | --- |
| Business profile | What the business sells, customers and value propositions |
| Product ICP | Industries, company sizes, buyer roles, pains and disqualifiers |
| Prospect research | Evidence-based summary, ICP match and local embedding similarity |
| Buying signals | Typed signals, evidence and confidence |
| Problem statement | Product-relevant pain hypothesis and supporting evidence |
| Prospect scoring | Model-generated 0-100 score, priority and explanation |
| Personalised email | Subject and body, saved as a draft |
| Reply classification | Interested / Not interested / Later / Unsubscribe / Other |

## Reliability and local boundary

- The only inference transport is `local_sales/llm_client.py`, fixed to `http://127.0.0.1:11434`. Proxies and redirects are disabled. Model choices are allowlisted local Qwen3 tags.
- Every model attempt is recorded with task, product, model, source, timestamp, duration, status and runtime-reported token counts. Missing token counts remain null.
- JSON schema-constrained responses are checked with Pydantic; malformed responses get at most three attempts.
- Ollama outages or missing models leave tasks waiting in SQLite. Pending work is rechecked periodically and recovers after restart. Permanent generation failures require an explicit retry.
- Editing source inputs cancels stale work and increments the product revision; in-flight results for older revisions are discarded.
- Embeddings load **only** from `models/all-MiniLM-L6-v2`, with offline flags and `local_files_only=True`. Missing files cause an actionable failure, never an automatic download.
- The dashboard binds to loopback. Same-origin writes and trusted host checks help protect the local API. It is a single-user local app without authentication.

## Test and verify

```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --check local_sales/web/app.js
.\.venv\Scripts\python.exe scripts/audit_local.py
```

The automated tests use labelled scripted responses in `tests_local/` to test failure handling deterministically. They are not a substitute for real-model or physically disconnected acceptance testing.

See [verification and offline test instructions](docs/local-verification.md), [architecture](docs/local-architecture.md), [licences and costs](docs/local-licenses.md), [upstream audit](docs/local-upstream-audit.md), and [demo guide](docs/local-demo.md).

## Source provenance

This checkout preserves the history of `ethanplusai/harvey` (now renamed Sellbird), pinned to MIT-licensed tag **v0.3.0**, commit `e2632eb20ee2d4fb6fe04ae715a52f578acf9a37`. The original [LICENSE](LICENSE) is retained. Bundled Geist and Newsreader fonts were reused; see their font licence notices.

The implementation lives in **`local_sales/`**. Unused original runtime code, tests, prompts, skills and obsolete documentation were removed using the reviewed 94-file cleanup plan. The original Git history, MIT licence and separately vendored fonts remain. The supported entry point is **`harvey-local`** or **`python -m local_sales.cli`**.

The source audit checks both the executable local package and repository text files, excluding Git history, downloaded environments/models, user data and generated evidence. Its machine-readable report is `output/runtime-audit.json`.

## Known limitations

- CPU inference is slow; large batches can take substantial time. Results depend on model quality and supplied evidence.
- No public-web research, enrichment services, mailbox connections, sending, multi-user authentication or hosted deployment is included.
- NVIDIA GPU detection is best effort. Integrated GPUs are not treated as dedicated inference GPUs. Model selection is conservative: below 8 GB RAM use 1.7B; ordinary 8-24 GB CPU machines use 4B; 24 GB RAM or 8 GB VRAM qualifies for 8B.
- Data stays on the machine but the checkout is currently inside OneDrive. Move it outside synchronised folders if OS-level cloud synchronisation is unwanted.
- The supplied demo includes a disconnected test according to the submitter. Its contents and exact revision match have not been independently verified; historical test records retain their original limitations.

## Other operating systems

The Python app is portable; the bundled setup scripts target Windows. On Linux/macOS, create a Python environment, install `requirements-local.txt`, install Ollama from its official distribution, download the chosen Qwen3 model, and run `scripts/download_embeddings.py` once. Start Ollama with `OLLAMA_NO_CLOUD=1`, then run `python -m local_sales.cli`. Cross-platform automated tests passed in GitHub CI on Windows and Ubuntu with Python 3.11 and 3.13. Full real-model installation was tested on the Windows development machine.
