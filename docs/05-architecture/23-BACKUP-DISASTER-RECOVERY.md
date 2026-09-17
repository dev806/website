# Backup & Disaster Recovery Architecture Specification

**Document ID:** `DOC-ARCH-023`  
**Classification:** DevOps & Business Continuity / Phase 4 Disaster Recovery  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [Database Architecture](file:///d:/Project_website/docs/05-architecture/05-DATABASE-ARCHITECTURE.md) | [Security Architecture](file:///d:/Project_website/docs/05-architecture/14-SECURITY-ARCHITECTURE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Business Continuity Architecture: Capability vs. Policy

In strict accordance with project governance:
> **GOVERNANCE LAW:** No binding operational SLA, contractual recovery commitment, or numerical RPO/RTO metric is treated as an approved production requirement without explicit Project Owner ratification.

The architecture explicitly differentiates between four continuity dimensions:

1. **Backup Capability (Engineering Primitive)**: Native Microsoft SQL Server capabilities supporting Full (`BACKUP DATABASE`), Differential (`WITH DIFFERENTIAL`), and Transaction Log (`BACKUP LOG`) point-in-time archives.
2. **Restore Capability (Validation Primitive)**: Procedural capability to restore databases to arbitrary recovery points, verifiable via `RESTORE VERIFYONLY` and automated validation databases (`DBCC CHECKDB`).
3. **Recovery Planning (Incident Runbooks)**: Prescribed step-by-step technical procedures for recovering from local developer environment corruption or cloud host failures (Section 3).
4. **Final RPO / RTO Policy (`PROPOSED / POLICY DECISION REQUIRED`)**:
   - Numerical Recovery Point Objective (RPO) and Recovery Time Objective (RTO) targets are **candidate engineering proposals only**, requiring explicit business and operational policy ratification before production launch:
     - *Candidate RPO*: Unratified proposal $< 4\text{ hours}$ (`PROPOSED / POLICY DECISION REQUIRED`).
     - *Candidate RTO*: Unratified proposal $< 2\text{ hours}$ (`PROPOSED / POLICY DECISION REQUIRED`).

---

## 2. Microsoft SQL Server Backup Strategy (Candidate Schedule)

Microsoft SQL Server provides native, enterprise-grade backup primitives executed via T-SQL scripts or automated Maintenance Plans in SSMS:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        SQL SERVER BACKUP SCHEDULE (CANDIDATE)                          │
├───────────────────────┬────────────────────────────┬───────────────────────────────────┤
│ BACKUP TIER           │ FREQUENCY                  │ RETENTION & STORAGE POSTURE       │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Full Database Backup  │ Daily at 02:00 UTC         │ Candidate: 30 days (AES-256       │
│ (`BACKUP DATABASE`)   │                            │ encrypted; off-site transfer).    │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Differential Backup   │ Every 6 Hours              │ Candidate: 7 days (captures all   │
│ (`WITH DIFFERENTIAL`) │                            │ pages modified since last full).  │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Transaction Log Backup│ Every 1 Hour (Production)  │ Candidate: 48 hours (point-in-time│
│ (`BACKUP LOG`)        │ (If Full Recovery Model)   │ recovery precision).              │
└───────────────────────┴────────────────────────────┴───────────────────────────────────┘
```

### Local T-SQL Backup Routine (SSMS)
```sql
-- Conceptual Daily Backup Script
BACKUP DATABASE StudioWebsiteDev 
TO DISK = 'C:\Backups\StudioWebsiteDev_Full.bak'
WITH FORMAT, COMPRESSION, STATS = 10,
NAME = 'Full-StudioWebsiteDev-Backup';
GO
```

---

## 3. Disaster Scenarios & Incident Recovery Playbooks

### Scenario 1: Local Development Database Corruption / Accidental Drop
* **Impact**: Loss of local diagnostic session records.
* **Recovery Action**:
  1. Re-run `CREATE DATABASE StudioWebsiteDev;` in SSMS.
  2. Execute `alembic upgrade head` to recreate all relational tables and indexes.
  3. Re-seed static solution catalogs. Total recovery time: $< 2$ minutes.

### Scenario 2: Production Server / Host Failure
* **Impact**: Web application and database instance unreachable.
* **Recovery Action**:
  1. Spin up a replacement compute instance from the candidate Docker image.
  2. Pull the most recent encrypted full database backup and differential backup from off-site storage.
  3. Execute `RESTORE DATABASE ... WITH RECOVERY` in SQL Server.
  4. Update DNS records (Cloudflare / Route 53) to point to the new host IP.

---

## 4. Backup Verification & Restore Testing Drills

A backup is only as good as its tested restore:
1. **Automated Monthly Restore Drill**: On the first business day of every month, a scheduled script restores the latest production backup file into a dedicated validation database (`StudioWebsiteRestoreDrill`).
2. **Data Integrity Check**: Runs `DBCC CHECKDB` against the restored database to mathematically verify zero page corruption before declaring the backup valid.
