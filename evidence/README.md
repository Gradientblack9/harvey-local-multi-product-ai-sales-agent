# Local-model test evidence

These are historical measurements and outputs from real local Qwen3 4B inference on the two fictional seed products. They are published as evidence, not as pre-seeded runtime results or a claim that a new installation has already executed its workflows.

| File | What it demonstrates |
| --- | --- |
| [real-inference.json](real-inference.json) | All eight workflow types completed; distinct product ICPs; actual model outputs and per-attempt inference logs. Only sample product IDs 1 and 2 are included. |
| [runtime-outage.json](runtime-outage.json) | A task waited while the project-owned Ollama service was stopped, saved data stayed accessible, and generation completed after restart. |
| [source-audit.json](source-audit.json) | Source scan of the local implementation, including the scan scope and exclusions. This is a source audit, not packet capture. |
| [verification-summary.json](verification-summary.json) | Historical test/build provenance and honest status of the outstanding physical offline test and video. |

The non-loopback socket guard in the real-inference report applied to the verification process during the second-product comparison. Physical Wi-Fi remained enabled, and the separate Ollama process was not placed under a system-wide firewall rule by that guard. The physical disconnected acceptance test and screen recording are still required.

Model output should be reviewed for unsupported assumptions before using it in sales outreach. No real emails were sent.
