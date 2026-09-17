# DevOps & Production Deployment Strategy (Candidate Evaluation)

**Document ID:** `DOC-ARCH-022`  
**Classification:** DevOps & Infrastructure / Phase 4 Deployment Strategy  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [ADR-014](file:///d:/Project_website/docs/05-architecture/02-ARCHITECTURE-DECISION-RECORDS.md#adr-014)  
**Status:** CANONICAL SPECIFICATION (PRODUCTION DECOUPLED & OPEN)  

---

## 1. Governance Mandate: Production Hosting Decoupled

In strict accordance with Owner Decision `BD-015` and `CST-CNF-008`:
> **BINDING PRINCIPLE:** The production hosting provider and production database engine **remain intentionally open, unfinalized, and decoupled from local development**. 

Local development runs on **Windows + Microsoft SQL Server + Uvicorn (₹0)**. Production deployment options are evaluated here as **candidates** to guide future deployment planning without prematurely committing the studio to paid cloud infrastructure.

---

## 2. Comparative Evaluation of Production Hosting Candidates (Evaluation Only)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION HOSTING CANDIDATE COMPARISON                         │
├───────────────────────┬────────────────────┬────────────────────┬──────────────────────┤
│ EVALUATION CRITERIA   │ CANDIDATE A:       │ CANDIDATE B:       │ CANDIDATE C:         │
│                       │ Linux VPS + Docker │ Managed PaaS       │ Enterprise Cloud     │
│                       │ (Hetzner / DO)     │ (Render / Railway) │ (AWS / Azure)        │
├───────────────────────┼────────────────────┼────────────────────┼──────────────────────┤
│ Infrastructure Cost   │ COST EVALUATION    │ COST EVALUATION    │ COST EVALUATION      │
│ Posture               │ REQUIRED           │ REQUIRED           │ REQUIRED             │
│ Operational Overhead  │ Moderate (Linux OS)│ Very Low (Git push)│ High (IAM/VPC/Config)│
│ Database Portability  │ Full Docker control│ Managed container  │ Managed SQL / RDS    │
│ Automated SSL/TLS     │ Caddy automatic    │ Built-in PaaS SSL  │ AWS ACM / CloudFront │
│ Deployment Complexity │ Low (Docker Compose│ Lowest             │ High                 │
│ Vendor Lock-In Risk   │ Zero (Standard OCI)│ Low                │ Moderate             │
├───────────────────────┼────────────────────┼────────────────────┼──────────────────────┤
│ Architecture Status   │ PROPOSED CANDIDATE │ PROPOSED CANDIDATE │ DEFERRED (Future)    │
└───────────────────────┴────────────────────┴────────────────────┴──────────────────────┘
```

---

## 3. Candidate Containerization Specification (Conceptual Dockerfile)

*(Note: Architectural specification only. Zero Docker containers or images are built during this documentation phase).*

```dockerfile
# Multi-stage Python 3.12 Minimal Build Pattern
FROM python:3.12-slim AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl gnupg2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Minimal Runtime Stage
FROM python:3.12-slim AS runner
WORKDIR /app

# Install MS ODBC Driver 18 for Linux persistence
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg2 unixodbc \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Run as non-root unprivileged service user
RUN useradd -m -u 1001 studio
USER studio

COPY --from=builder /root/.local /home/studio/.local
COPY --chown=studio:studio ./app ./app
COPY --chown=studio:studio ./templates ./templates
COPY --chown=studio:studio ./static ./static

ENV PATH=/home/studio/.local/bin:$PATH
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

---

## 4. Reverse Proxy & Ingress Architecture (Caddy / Nginx)

In a production VPS topology:
1. **Reverse Proxy (Caddy / Nginx)**: Binds to external ports 80/443.
2. **Automated SSL/TLS**: Caddy automatically provisions and renews Let's Encrypt certificates without manual certbot scripting.
3. **Internal Forwarding**: Proxies incoming traffic to Uvicorn at `http://127.0.0.1:8000`.
4. **Static File Optimization**: Serves static CSS, JS, and image files directly from disk cache, offloading Uvicorn worker threads.
