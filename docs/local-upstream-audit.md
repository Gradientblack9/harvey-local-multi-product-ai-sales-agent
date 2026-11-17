# Upstream adaptation and audit

Base repository: https://github.com/ethanplusai/harvey (redirects to Sellbird).
Base tag: **v0.3.0**.
Base commit: **e2632eb20ee2d4fb6fe04ae715a52f578acf9a37**.
Base licence: MIT, verified from the checked-out LICENSE. Current upstream uses a different licence; this build is based on the pinned MIT revision.

## Original boundaries found

The original thinking engine invoked subscription-backed model command-line providers. A secondary adapter implemented another subscription runtime. Original trainer, agents and setup code called those engines. Original integrations included sending, mailbox and online prospect data paths. The original dashboard was wired to those wider integrations.

The adaptation replaces the runtime with the `local_sales` package. It reuses the font assets, retains the original MIT attribution and Git history, introduces product-scoped storage, local inference, strict output schemas and a dashboard tailored to the eight requested workflows. `pyproject.toml` only packages `local_sales*`; requirements only install the local app's dependencies. CI now tests the local package with deterministic transport stubs; tests themselves never invoke a subscription provider.

## Audit scope

`python scripts/audit_local.py` scans all executable Python/JavaScript/HTML/CSS in `local_sales` for the PRD provider terms plus the original subscription-provider command names. It also checks repository text files against the four PRD grep terms and reports any surviving legacy matches. The output is `output/runtime-audit.json`. Git history, downloaded environments/models, data, generated evidence and caches are excluded.

This is a source-level audit, not packet capture. Real inference logs independently record loopback endpoints. Embedding loading is separately constrained to local files. Setup-only scripts are intentionally allowed to download official dependencies and models.

## Completed legacy cleanup

The reviewed 94-file cleanup plan was explicitly approved and completed. Each path was checked to stay inside the checkout, and its SHA-256 had to match the reviewed file before removal. The manifest is retained as `legacy-cleanup-plan.json`.

Unused original runtime, test, prompt, skill and obsolete documentation files were removed. Git history, the original MIT `LICENSE`, local code, local tests, local documentation and separately vendored fonts and notices remain. The original code can be inspected from the pinned Git revision without placing a cloud-dependent runtime in the current source tree.
