# Verification and remaining acceptance evidence

## Automated checks

The deterministic suite in `tests_local/` verifies:

- Product and prospect isolation, including cross-product IDs rejected before queue insertion.
- Seed data includes inputs only.
- Product/prospect editing, revisions, stale-result rejection and downstream invalidation.
- Queue deduplication, missing-model waiting, resume, failed dependencies and restart recovery.
- Schema validation, three-attempt limit, invalid confidence/score rejection, and per-attempt logs.
- Fixed loopback inference, refusal to follow redirects and rejection of non-allowlisted model tags.
- Missing embedding checkpoint fails without initiating a download.
- Same-origin writes, trusted hosts, local asset loading and formula-safe CSV export.
- Conservative hardware recommendation.

Run `python -m pytest -q`. In environments with restricted temporary directories, set a writable `--basetemp` inside the checkout. Tests use scripted responses solely in the test directory; actual product outputs use Ollama.

## Real model verification

Run one full pipeline from the dashboard with one prospect and one reply thread, then run:

```powershell
.\.venv\Scripts\python.exe scripts/verify_real.py
```

The script requires actual completed tasks covering all eight workflow types in product 1. It generates product 2's business profile and ICP through the same local inference client and captures schema-validated outputs, logs and distinct product ICPs in `output/real-inference-evidence.json`.

During the second-product comparison, a process-level socket/DNS guard rejects non-loopback connections. An intentional documentation-address probe demonstrates rejection. **This is not a claim that Wi-Fi was physically disconnected, nor does it impose a system-wide firewall policy on the separate Ollama process.** The portable Ollama service is separately started with cloud functionality disabled, and only local model tags are used.

## Physical offline acceptance run

1. Complete setup and confirm both model indicators are ready.
2. Save a Git commit so the tested version is identifiable.
3. Disconnect Wi-Fi/Ethernet using the OS. Keep localhost available.
4. Run a fresh pipeline on one prospect and one saved reply, covering all eight workflows.
5. Verify the task queue reaches completed. Export logs and the workspace; capture screenshots.
6. Stop **the project-owned Ollama process only** using its recorded PID or its original terminal. Queue another profile task. Confirm waiting/error status while editing products and browsing saved results still work.
7. Restart the project runtime and confirm the waiting task resumes. Export the recovery logs.
8. Record the OS disconnected state and a network capture/process connection listing during inference, then restore network connectivity.

Do not claim this manual test passed unless it was actually performed and recorded. The app itself cannot infer physical internet disconnection from a successful localhost call.

## Submission checklist

- [x] Literal repository text/provider scan clean after approved legacy cleanup (excluding Git history, downloaded packages/models, user data and generated evidence).
- [ ] Physical disconnected run of all eight workflows recorded.
- [x] Outage and recovery demonstrated with the real runtime stopped/restarted.
- [x] Two distinct product ICPs and product-scoped outputs shown.
- [x] Tests, source audit, licence table, cost statement and limitations included.
- [ ] A user-owned remote fork with the tested commit published.
- [ ] Final 5-10 minute screen recording matches that exact commit.

Actual results from this build are summarised in `output/build-verification.json`; check its status fields rather than treating this checklist as evidence of completion.
