# Licences, models and cost statement

## Cost

The application uses no metered inference service and no subscription-backed model runtime. Token charges are **$0**. Setup downloads are free to obtain from their official sources. Electricity, hardware, disk space and internet connectivity are ordinary user costs and are not claimed to be zero. No email sending or paid enrichment is included.

## Component licences

| Component | Licence | Verification source |
| --- | --- | --- |
| Harvey v0.3.0 base | MIT | Original [LICENSE](../LICENSE), commit `e2632eb20ee2d4fb6fe04ae715a52f578acf9a37` |
| Local application code | MIT | Inherits the project licence and preserves upstream attribution |
| Python | PSF licence | [Python licence](https://docs.python.org/3/license.html) |
| FastAPI / Pydantic | MIT | Installed package metadata in the dependency inventory |
| Uvicorn / Starlette / HTTPX | BSD-3-Clause | Installed package metadata in the dependency inventory |
| SQLite | Public domain | [SQLite copyright statement](https://sqlite.org/copyright.html) |
| psutil | BSD-3-Clause | Installed package metadata |
| Sentence Transformers | Apache-2.0 | Installed package metadata |
| Transformers | Apache-2.0 | Installed package metadata |
| PyTorch | BSD-3-Clause | Installed package metadata; redistributed binaries include their own dependency notices |
| Ollama runtime v0.40.16 | MIT | [Official licence](https://github.com/ollama/ollama/blob/v0.40.16/LICENSE); portable archive includes additional native-library notices |
| Qwen3 4B and configured Qwen3 family | Apache-2.0 | [Official model entry](https://ollama.com/library/qwen3:4b) and downloaded model licence layer |
| all-MiniLM-L6-v2 | Apache-2.0 | [Model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) |
| Geist / Geist Mono | SIL Open Font License 1.1 | [Bundled Geist notice](../local_sales/web/fonts/geist-OFL.txt), [Geist Mono notice](../local_sales/web/fonts/geistmono-OFL.txt) |
| Newsreader | SIL Open Font License 1.1 | [Bundled notice](../local_sales/web/fonts/newsreader-OFL.txt) |

`local-dependency-inventory.json` records installed versions, declared licence fields and project URLs for the resolved Python dependency closure. `requirements-verified.txt` captures the versions from the Windows Python 3.13 verification environment; it is a platform-specific snapshot. The direct application dependency versions are pinned in `pyproject.toml` and `requirements-local.txt`. Package metadata is not a substitute for inspecting all notices when redistributing third-party binary bundles.

Model and runtime files live in ignored `models/` and `.runtime/` folders and are not committed to Git. The portable runtime downloader is pinned to the tested Ollama release and checks the release asset's SHA-256 digest when the official metadata supplies one; it records the downloaded digest in `.runtime/release.json`. Embedding weights are downloaded by a separate setup-only script and saved locally.

## Hardware

The build machine reported approximately 15.7 GB RAM, 10 physical cores / 12 logical threads, and no NVIDIA GPU. Ollama detected an Intel integrated GPU but selected CPU execution. The default is Qwen3 4B with a 4096-token context and one concurrent generation. Call durations in exported inference logs are the actual measurements; the UI does not invent throughput figures.

The PRD suggests 8B at 16 GB RAM or with a GPU. This build makes a documented conservative adjustment: 4B on ordinary CPU systems with 8-24 GB RAM, 1.7B below 8 GB, and 8B when at least 24 GB RAM or 8 GB dedicated VRAM is detected. This leaves room for the OS, browser and embedding model. Users can explicitly choose any supported local Qwen3 size after downloading it.
