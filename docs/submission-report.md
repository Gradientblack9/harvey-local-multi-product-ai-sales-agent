# Harvey Local submission report

EDXSO AI Engineer Intern Assignment 2 | 19 November 2026

## 1 Submission overview

Harvey Local is a locally runnable, multi-product AI sales application. It combines product configuration, business understanding, prospect analysis, outreach drafting and reply classification in one browser dashboard. Python and FastAPI coordinate a persistent SQLite queue; Ollama runs Qwen3 on the user's computer. Sentence Transformers supplies local embeddings. No paid inference service, external model endpoint, token billing or coding-assistant subscription is required to run the application.

This report accompanies the source repository and demonstration recording. It covers setup, architecture, implementation decisions, all eight workflows, model selection, costs, licences, evidence and limitations. Delivery is a documented local installation; no public application deployment is supplied.

| Deliverable | Location or status |
| --- | --- |
| Source repository | [GitHub repository](https://github.com/Gradientblack9/harvey-local-multi-product-ai-sales-agent) |
| Submission branch | assignment-2, the repository default branch |
| Video demonstration | [Watch the submitted demo](https://drive.google.com/file/d/1yE9wX_hgOdah1AvPohjAdwIcLFRORUrx/view?usp=sharing) |
| Working application | Local browser at http://127.0.0.1:8000 after setup and launch |
| Technical report | This report and the detailed documents in docs/ |
| Logs and sample outputs | [Published evidence](https://github.com/Gradientblack9/harvey-local-multi-product-ai-sales-agent/tree/assignment-2/evidence) |
| Application revision | 1be8dd22909d07211c1c4f82a69924ffc571c026; this submission update changes documentation and evidence only |

The submitter confirmed that the supplied demo includes the internet-disconnected test. The recording's accessibility, length, individual workflow coverage and exact recorded commit have not been independently verified. Earlier machine-readable evidence explicitly records that its original run left Wi-Fi enabled; it must not be mistaken for the later video demonstration.

## 2 Assignment coverage

| Assignment requirement | Implementation and verification |
| --- | --- |
| Fork and extend Harvey | Genuine upstream fork with history and MIT v0.3.0 attribution retained |
| Zero paid or cloud inference | Fixed loopback model client, allowlisted local models, cloud disabled in startup, no paid fallback |
| Local architecture | Ollama, Qwen3, SQLite, Python, FastAPI and local Sentence Transformers |
| Dashboard | Buildless HTML, CSS and JavaScript implementation; plain black and white, Times New Roman |
| Multiple products | Product-scoped configuration, ICPs, prospects, results, tasks and inference logs |
| Eight sales workflows | Implemented and represented in historical real-model evidence |
| Hardware awareness | RAM and CPU detection, best-effort NVIDIA VRAM detection, conservative model recommendations |
| Failure handling | Waiting queue, continued saved-data browsing and recovery when Ollama returns |
| Offline acceptance | Submitter confirms disconnected test in linked video; historical process guard is separate evidence |
| Public-web research tooling | Not implemented; research currently uses previously stored local data |
| Reproducible delivery | Windows setup and launcher, pinned direct dependencies, README and CI |
| Licensing and costs | Component statements plus resolved package inventory and licence appendix |
| Demo and evidence | Supplied video, real inference logs, outage evidence and automated checks |

The assignment allows an equivalent implementation. This submission uses a buildless browser UI instead of React. The absence of the prescribed public-web collection tools is a disclosed gap; local-data research implements the offline research workflow but does not provide fresh external discovery.

## 3 Source provenance and design decisions

The starting repository is ethanplusai/harvey, now renamed ethanplusai/sellbird. This implementation is based on MIT-licensed tag v0.3.0, commit e2632eb20ee2d4fb6fe04ae715a52f578acf9a37. The original LICENSE and Git history are preserved. The upstream default branch has a different licence; the licence statement here applies to the pinned base used for this application.

The active implementation lives in local_sales/. Unused original runtime files were removed through the reviewed legacy cleanup plan. A single inference client makes the local boundary easy to inspect. A single queue worker limits memory contention on ordinary laptops. SQLite provides persistence without an external database service. A buildless dashboard keeps installation simple and avoids external frontend assets.

Runtime and model downloads are setup operations. Model files, the portable runtime, the virtual environment and the user's database are excluded from source control. The repository publishes only fictional sample evidence, not personal workspace data.

## 4 Architecture and storage

Browser dashboard -> FastAPI on 127.0.0.1:8000 -> SQLite durable queue -> single worker -> local inference client -> Ollama on 127.0.0.1:11434. The worker also loads the local embedding checkpoint. Results, task states and inference logs return to SQLite and are displayed by the dashboard.

| Module | Responsibility |
| --- | --- |
| app.py and web/ | API, lifecycle, local assets, exports and dashboard |
| config.py | Fixed endpoint, allowed model tags, local paths and offline embedding flags |
| db.py and seed.py | SQLite schema, transactions, input revisions and fictional sample inputs |
| workflows.py | Task dependencies, serial execution, waiting, retries and stale-result protection |
| llm_client.py and schemas.py | Schema-constrained model calls, validation and per-attempt logs |
| embeddings.py and hardware.py | Local similarity model and hardware recommendations |

SQLite uses WAL and foreign keys. products owns company/product inputs and a revision; icps stores the current ICP. prospects stores source notes and generated research, problem and score. signals, emails and replies use product-scoped prospect references. task_queue records dependencies, revision, model, attempts and results. inference_logs records actual generation attempts. settings stores the selected model.

Every prospect operation includes a product ID. The API rejects cross-product IDs, and composite database constraints prevent cross-product child records. Changing product or prospect inputs invalidates dependent outputs and cancels stale work. A result arriving after a revision change is discarded rather than saved against new inputs.

## 5 Sales workflows and product experience

| Workflow | Inputs and generated output |
| --- | --- |
| Business profile | Locally stored company/product details -> business summary and value propositions |
| Product ICP | Product context -> industries, sizes, buyer roles, pains and disqualifiers |
| Prospect research | Stored prospect notes and ICP -> evidence summary, fit and embedding similarity |
| Buying signals | Prospect research -> typed signals with evidence and confidence |
| Problem statement | Research and signals -> product-relevant pain hypothesis |
| Prospect scoring | Prior analysis -> score from 0 to 100, priority and explanation |
| Personalised email | Product and prospect analysis -> subject and body saved as a draft |
| Reply classification | Sample conversation -> Interested, Not interested, Later, Unsubscribe or Other |

The main dependency chain is profile -> ICP -> research -> signals -> problem -> scoring -> email. Reply classification is a separate branch. Missing prerequisites are enqueued automatically, and matching pending tasks are deduplicated. There is no email sending or mailbox integration.

The dashboard provides product selection and editing, prospect search and selection, workflow actions, email drafts, replies, task status, inference logs and settings. CSV and JSON exports support review. The two seed products are Sentinel, for access governance, and Relay, for support operations. There are 24 fictional prospect records and 10 fictional reply threads across those products.

Seed data contains inputs only. A fresh installation does not seed generated profiles, ICPs, scores or email drafts. Production output comes from the local model. Scripted responses exist only in automated tests and never act as a production fallback.

## 6 Installation and evaluator walkthrough

Use Windows with Python 3.11 or newer, Git, and at least 12 GB of free disk space. A 16 GB laptop is the ordinary configuration. Internet is needed for the first dependency, runtime and model downloads. Use a folder outside OS-synchronised storage when strict machine-only storage is required.

```powershell
git clone https://github.com/Gradientblack9/harvey-local-multi-product-ai-sales-agent.git
cd harvey-local-multi-product-ai-sales-agent
powershell -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Setup creates .venv, installs pinned direct dependencies, downloads portable Ollama and the embedding checkpoint, pulls qwen3:4b and initialises the database. After setup, double-click Start Harvey.cmd or run start.ps1. Keep the console open and visit http://127.0.0.1:8000. A browser tab alone does not start the server. If the browser reports ERR_CONNECTION_REFUSED, start the application before refreshing.

Select Sentinel, inspect the product details, and run the pipeline for one prospect. Follow Task Queue until completion, then inspect all generated outputs and a sample reply classification. Open Inference Logs to review the task, product, model and timing. Switch to Relay and compare its ICP and results. Large CPU batches take time; begin with one prospect.

Use Ctrl+C to stop the dashboard. SQLite preserves data between launches. The portable Ollama service may remain running; its project-owned PID is recorded in .runtime/ollama.pid. Run only one dashboard worker per database. On Linux/macOS, install the Python requirements and Ollama separately, download the embedding checkpoint using scripts/download_embeddings.py, set OLLAMA_NO_CLOUD=1 and run python -m local_sales.cli. The packaged setup scripts target Windows.

## 7 Hardware and model configuration

| Hardware | Recommendation |
| --- | --- |
| Below 8 GB RAM | qwen3:1.7b; close other applications and benchmark memory use |
| 8 to below 24 GB RAM without 8 GB dedicated VRAM | qwen3:4b; standard laptop configuration |
| At least 24 GB RAM or 8 GB dedicated VRAM | qwen3:8b; larger-model configuration |

The allowed tags are qwen3:0.6b, qwen3:1.7b, qwen3:4b and qwen3:8b. For a different initial model, run setup.ps1 -Model qwen3:1.7b or setup.ps1 -Model qwen3:8b. A model must be downloaded before selecting it for offline use. The default runtime uses a 4096-token context and one concurrent generation.

The development machine reported about 15.7 GB RAM, 10 physical cores and 12 logical threads, with no NVIDIA GPU. Ollama selected CPU execution. Dedicated NVIDIA detection is best effort; integrated graphics are not assumed to provide usable dedicated VRAM. The 24 GB threshold is deliberately conservative to leave memory for the OS, browser and embeddings. Recommendations do not guarantee throughput or prevent memory pressure on every host.

## 8 Local boundary and failure behaviour

All generation uses the fixed loopback endpoint http://127.0.0.1:11434 through llm_client.py. The HTTP client ignores proxy environment variables and rejects redirects. Only allowlisted local Qwen3 tags can be used. The project startup sets OLLAMA_NO_CLOUD=1. An independently started Ollama service must also be configured appropriately.

The embedding model loads from models/all-MiniLM-L6-v2 using offline flags and local_files_only=True. Missing weights cause an actionable error, not an automatic download. The UI uses local assets and same-origin connections. No external research, enrichment or sending service is wired into the runtime.

When Ollama is unavailable or a model is missing, tasks wait in SQLite and retry availability periodically. Saved data can still be browsed and edited. Interrupted tasks are recovered when the app restarts. Invalid generated JSON is checked against Pydantic schemas and retried at most three times. Permanent failures remain visible; failed prerequisites block dependent tasks until an explicit retry succeeds.

The app is single-user and binds to loopback. It has trusted-host checks, same-origin write checks, a restrictive content policy and formula-safe CSV export. It has no authentication or database encryption and should not be exposed directly to the public internet. Operating-system folder synchronisation is outside the application's network boundary.

## 9 Test evidence and offline demonstration

On 19 November 2026, the automated suite passed 18 tests in 4.39 seconds against application revision 1be8dd2. The source audit passed with zero active runtime matches and zero repository matches within its documented scope. Tests cover isolation, input invalidation, queue recovery, validation, loopback restrictions, missing embeddings and local security checks.

GitHub CI also passed on that application revision across Windows and Ubuntu with Python 3.11 and 3.13. See [the successful CI run](https://github.com/Gradientblack9/harvey-local-multi-product-ai-sales-agent/actions/runs/44512067973). CI uses test fixtures and does not download or run the language model.

| Evidence | What it supports |
| --- | --- |
| evidence/real-inference.json | Actual local Qwen3 4B outputs for all eight workflows and distinct product ICPs |
| evidence/runtime-outage.json | Waiting during a real Ollama outage, saved-data browsing and recovery |
| evidence/source-audit.json | Historical source audit with scope and exclusions |
| evidence/verification-summary.json | Historical build and test provenance; original offline test limitations |
| evidence/submission-status.json | Current demo link, submitter confirmation and documentation update status |

One recorded business-profile call used qwen3:4b at the loopback /api/chat endpoint, took 53,691 ms, and reported 496 prompt tokens and 265 completion tokens. These are measured runtime figures, not estimated throughput or billed tokens. Logs retain task/product IDs, timestamps, model, local source, duration, status and available token counts.

The historical network guard blocked a non-loopback probe inside the verification process. Wi-Fi stayed enabled, and the guard did not constrain the separate Ollama process. The submitter has since supplied the demo link and confirmed that it includes the disconnected test. This report does not independently certify the recording's full coverage or exact source revision.

To reproduce acceptance, finish setup, record git rev-parse HEAD, disconnect Wi-Fi/Ethernet, then generate fresh results for all eight workflows using local data. Show the OS disconnected state, completed task records and inference logs. Stop only the project-owned Ollama service, queue a task, verify waiting and continued browsing, then restart it and show recovery. Preserve the logs and restore connectivity afterward.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/audit_local.py
```

## 10 Costs and licences

The application has no metered inference service, per-token charge, paid prospecting API or subscription-backed agent runtime. Token charges are $0. Hardware, electricity, storage and initial internet access remain user costs. No account credentials are needed for local generation. Development assistance is not a runtime dependency.

| Component | Licence and source |
| --- | --- |
| Harvey v0.3.0 and local code | MIT; retained repository LICENSE and pinned base commit |
| Python | PSF licence; installed interpreter notices |
| SQLite | Public domain; SQLite copyright statement |
| Ollama v0.40.16 | MIT; official tagged licence and downloaded runtime notices |
| Qwen3 models | Apache-2.0; official model entry and downloaded licence layer |
| all-MiniLM-L6-v2 | Apache-2.0; model card and checkpoint notices |
| FastAPI and Pydantic | MIT; installed package metadata |
| Uvicorn, Starlette, HTTPX and psutil | BSD-3-Clause; installed package metadata |
| Sentence Transformers and Transformers | Apache-2.0; installed package metadata |
| PyTorch | BSD-3-Clause; binary distributions include additional dependency notices |
| Bundled Geist and Newsreader fonts | SIL Open Font License 1.1; bundled notices; current UI uses system Times New Roman |

See docs/local-licenses.md for source links. Appendix A lists the 51 resolved Python packages. Exact metadata and licence-file paths are recorded in docs/local-dependency-inventory.json. requirements-verified.txt is the Windows verification snapshot; requirements-local.txt pins direct dependencies. Models and native binaries are downloaded during setup rather than redistributed in the source repository.

Not every transitive package is exclusively MIT, BSD or Apache licensed. In particular, certifi declares MPL-2.0 and tqdm declares MPL-2.0 AND MIT; NumPy and regex declare mixed licence expressions. These exceptions are disclosed rather than described as uniformly permissive. Native wheels and bundled runtime libraries retain their own third-party notices; the top-level inventory is not a full binary-level legal audit.

## 11 Limitations and final review

Fresh public-web discovery, Scrapy/BeautifulSoup/Playwright collection, paid enrichment, mailbox connections and email sending are not implemented. Research is based on local supplied evidence, and model conclusions need human review. CPU generation can be slow. GPU detection is limited, the database is unencrypted, and there is no multi-user authentication. Fresh-machine model installation has not been independently reproduced on every supported OS.

Fictional inputs and deterministic test fixtures are explicitly separated from production generation. Existing evidence is historical and does not mean a fresh installation has already generated its results. The video is supplied and its disconnected test is confirmed by the submitter; external viewing access, duration and exact revision match still need reviewer confirmation. No claim of complete assignment acceptance is made on the basis of documentation alone.

For evaluation, use the repository default branch, this report, the linked video and the evidence directory together. Ensure the Drive recording is accessible to the evaluation team. The final documentation commit retains the application code from revision 1be8dd2.

## Appendix A Resolved Python dependencies

The following inventory is the installed verification environment snapshot. Licence names come from package metadata, supplemented by installed licence files where metadata is incomplete. Tokenizers is checked against its official version-tagged licence. Package-level identifiers do not replace bundled third-party notices.

| Package | Version | Licence |
| --- | --- | --- |
| annotated-doc | 0.0.5 | MIT |
| annotated-types | 0.7.0 | MIT |
| anyio | 4.13.0 | MIT |
| certifi | 2026.5.20 | MPL-2.0 |
| charset-normalizer | 3.4.7 | MIT |
| click | 8.4.2 | BSD-3-Clause |
| cloudpickle | 3.1.2 | BSD-3-Clause |
| colorama | 0.4.6 | BSD-3-Clause |
| fastapi | 0.121.3 | MIT |
| filelock | 3.29.0 | MIT |
| fsspec | 2026.4.0 | BSD-3-Clause |
| h11 | 0.16.0 | MIT |
| httpcore | 1.0.9 | BSD-3-Clause |
| httpx | 0.28.1 | BSD-3-Clause |
| huggingface_hub | 0.36.2 | Apache-2.0 |
| idna | 3.17 | BSD-3-Clause |
| iniconfig | 2.3.0 | MIT |
| Jinja2 | 3.1.6 | BSD-3-Clause |
| joblib | 1.6.0 | BSD-3-Clause |
| MarkupSafe | 3.0.3 | BSD-3-Clause |
| mpmath | 1.3.0 | BSD-3-Clause |
| narwhals | 2.28.0 | MIT |
| networkx | 3.6.1 | BSD-3-Clause |
| numpy | 2.4.6 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| packaging | 26.2 | Apache-2.0 OR BSD-2-Clause |
| pillow | 12.0.0 | MIT-CMU |
| pluggy | 1.6.0 | MIT |
| psutil | 7.1.3 | BSD-3-Clause |
| pydantic | 2.12.4 | MIT |
| pydantic_core | 2.41.5 | MIT |
| Pygments | 2.20.0 | BSD-2-Clause |
| pytest | 9.0.1 | MIT |
| PyYAML | 6.0.3 | MIT |
| regex | 2026.5.9 | Apache-2.0 AND CNRI-Python |
| requests | 2.34.2 | Apache-2.0 |
| safetensors | 0.8.0 | Apache-2.0 |
| scikit-learn | 1.9.1 | BSD-3-Clause |
| scipy | 1.18.1 | BSD-3-Clause |
| sentence-transformers | 5.1.2 | Apache-2.0 |
| setuptools | 81.0.0 | MIT |
| starlette | 0.50.0 | BSD-3-Clause |
| sympy | 1.14.0 | BSD-3-Clause |
| threadpoolctl | 3.8.0 | BSD-3-Clause |
| tokenizers | 0.22.2 | Apache-2.0 |
| torch | 2.12.0 | BSD-3-Clause |
| tqdm | 4.67.3 | MPL-2.0 AND MIT |
| transformers | 4.57.6 | Apache-2.0 |
| typing-inspection | 0.4.2 | MIT |
| typing_extensions | 4.15.0 | PSF-2.0 |
| urllib3 | 2.7.0 | MIT |
| uvicorn | 0.38.0 | BSD-3-Clause |
