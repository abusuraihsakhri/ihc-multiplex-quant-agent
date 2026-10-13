# IHC Multiplex Quant Agent

Research-oriented tools for summarizing multiplex immunohistochemistry (IHC) cell counts, PD-L1 positivity, and spatial cell-coordinate data.

## Browser calculator

The static application is in [`web/`](web/) with a root redirect in `index.html` for GitHub Pages. It runs entirely client-side in JavaScript, without a Python runtime or backend service.

Enter six aggregate values: viable tumor cell count, PD-L1-positive tumor and immune cell counts, CD8 and FoxP3 counts, and analyzed tissue area in mm². Select **Calculate metrics** to obtain:

- PD-L1 combined positive score (CPS) and tumor proportion score (TPS).
- CD8 and FoxP3 cell densities per mm².
- CD8/FoxP3 count ratio (reported as undefined when the denominator is zero).
- JSON and CSV downloads containing the current inputs and calculated outputs.

The calculation uses `CPS = min(100, 100 × (positive tumor cells + positive lymphocytes/macrophages) / viable tumor cells)` and `TPS = 100 × positive tumor cells / viable tumor cells`. It validates non-negative whole-cell counts and requires at least 100 viable tumor cells for these illustrative scores. Results are **descriptive only**. Clinical scoring adequacy, tumor indication, assay selection, interpretation, and eligibility for treatment require independent validation.

The browser application does not analyze microscopy images, segment nuclei, load WSI files, or diagnose specimens. It does not upload inputs, call external APIs, or persist entered values. Use de-identified aggregate data.

## Python workflows

This repository also retains two command-line engines and REST interfaces:

- `python cli.py` operates the task-audit supervisor under `agents/` (audit, chat, batch, verify-audit, serve).
- `python -m ihc_multiplex_quant_agent.cli` runs the additional case-oriented coordinator. The installed command `ihc-multiplex-quant-engine` invokes this interface.
- `ihc_multiplex_quant_agent.pdl1_scorer` provides arithmetic CPS and TPS helpers; `spatial_analysis` computes centroid-distance summaries and grid hotspots.
- `ihc_multiplex.py` and `enrichment.py` contain legacy/experimental rule-based modules, not validated computational pathology pipelines.

These components are distinct from the browser calculator. The server requires a Python host and **cannot run within GitHub Pages**. Threshold rules and advisory statements in the legacy supervisor should not be treated as published clinical thresholds or validated diagnostic recommendations.

## Install and test

Python 3.9 or newer is required for the package; a compatible Pydantic v2 is installed as a core dependency.

```bash
python -m pip install -e '.[server,test]'
pytest -q
node --check web/quantify.js
node --check web/app.js
node --test web/quantify.test.cjs
```

The browser tests use Node.js 22. The static calculator runs in current Chromium, Firefox, and Safari versions with modern JavaScript support; automated browser compatibility testing has not been established.

Example task audit:

```bash
python cli.py audit --task-id TASK-001 --target SPECIMEN-01 --primary 28.5 --secondary 14.2 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The local API exposes `/health`, `/metrics`, `/api/audit`, `/api/chat`, and `/api/audit/logs`; requests follow the `agents.models.SystemTaskPayload` schema.

## Security and limits

The browser application does not transmit data. The Python API provides heuristic pattern-based identifier checks; **these are not complete PHI de-identification or a guarantee of HIPAA compliance**. Do not submit identifiable patient information. Server audits use a keyed HMAC-SHA256 chain stored in process memory. Set a cryptographically random `AUDIT_SECRET_KEY` in the server environment. Each HMAC and chain link is checked, but in-memory logs do not establish durable, immutable provenance or detect deletion of the final entries.

Generate a secret and supply it using your deployment platform, without committing its value:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

For Docker Compose, supply `AUDIT_SECRET_KEY` in the host environment before running `docker compose up --build`. See `.env.example` for the expected variable.

## License

MIT — see [LICENSE](LICENSE).
