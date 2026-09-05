# IHC Multiplex Quant Agent

> **Domain:** Digital Pathology & Quantitative Histopathology  
> **Reference Guidelines & Standards:** College of American Pathologists (CAP) Synoptic Protocols & DICOM WSI

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**IHC Multiplex Quant Agent** is an analytical and computational platform implementing Multiplex Immunofluorescence Spatial Phenotyping (CD3/CD8/FoxP3/PD-L1). It provides multi-agent consensus evaluation, HMAC-SHA256 tamper-evident audit logging, and zero-PHI outbound data protection.

---

## ⚙️ Key Capabilities & Architecture

### Core Modules

- **`agents/supervisor.py`** — Master orchestrator coordinating multi-worker evaluations with PHI validation.
- **`agents/base.py`** — Enterprise security layer: Zero-PHI outbound guard, HMAC-SHA256 audit trail, and action executor.
- **`agents/workers.py`** — Specialized evaluation workers: `InvariantQCWorker`, `SafetyEscalationWorker`, `ProtocolConformanceWorker`.
- **`agents/models.py`** — Pydantic v2 schemas for task payloads, alerts, and consensus dossiers.
- **`agents/llm_factory.py`** — Pluggable LLM adapter supporting Ollama, Claude, OpenAI, and deterministic mock.
- **`agents/metrics.py`** — Prometheus metrics exporter for operational telemetry.
- **`agents/api.py`** — FastAPI REST server exposing `/health`, `/metrics`, `/api/audit`, `/api/chat`, `/api/audit/logs`.

### Domain Engines (enrichment.py)

- **`OverviewEngine`** — Baseline threshold monitoring.
- **`Enrichment1ImmuneHotcoldPhenotypeScoringWithSpatialContextEngine`** — Immune microenvironment classification.
- **`Enrichment2Pdl1CombinedPositiveScoreCpsComputationEngine`** — PD-L1 CPS per KEYNOTE guidelines.
- **`Enrichment3SpatialDistanceMatrixForTumorinfiltratingLymphocytesEngine`** — Spatial distance computation.
- **`Enrichment4Cd8foxp3RatioWithPrognosticStratificationEngine`** — CD8/FoxP3 prognostic scoring.

### Specialized Agents (ihc_multiplex.py, ihc_multiplex_quant_agent/)

- **`StainDeconvolutionAgent`** — Primary metric and stain quality auditor.
- **`NuclearSegmentationAgent`** — STAT kinetics and escalation auditor.
- **`SpatialImmunePhenotyperAgent`** — Biomarker concordance triager.

---

## 💻 Installation

```bash
pip install -e .
```

---

## 💻 CLI Usage

### 1. Run Single Audit
```bash
python cli.py audit --task-id TASK-001 --target SPECIMEN-01 --primary 28.5 --secondary 14.2 --status DISCORDANT
```

### 2. Query Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

---

## 🛡️ Security Architecture

- **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
- **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation. Set `AUDIT_SECRET_KEY` environment variable for persistent key material.
- **PHI Redaction:** Automatic redaction of detected identifiers in outbound responses.
- **LLM Agnostic Adapter:** Deterministic mock provider for testing; supports Ollama, Claude, and OpenAI for production.

---

## 🧪 Testing

Run the full test suite:

```bash
pytest -v
```

Run with coverage:

```bash
pytest -v --cov=agents --cov-report=term-missing
```

Execute high-throughput simulation benchmarks:

```bash
python simulator.py 100
```

---

## 🐳 Container Deployment

```bash
docker build -t ihc-multiplex-quant-agent .
docker run -p 8000:8000 ihc-multiplex-quant-agent
```

Or with Docker Compose:

```bash
docker-compose up
```

---

## 📊 Prometheus Metrics

The `/metrics` endpoint exposes operational counters:

- `system_tasks_total` — Total tasks processed
- `alerts_triggered_total` — Alerts by urgency tier
- `phi_outbound_blocks_total` — PHI interceptions
- `audit_chain_blocks_total` — Signed audit blocks
- `task_processing_duration_avg_seconds` — Average latency

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
