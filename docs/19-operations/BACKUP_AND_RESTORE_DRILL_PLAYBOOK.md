# Database Backup & Restore Drill Playbook

**Document ID:** `DOC-OPS-003`  
**Phase:** Phase 6.2.5 (Staging & Deployment Validation Foundation)  
**Status:** CANONICAL OPERATIONAL RUNBOOK  
**Governance Notice:** PROPOSED CANDIDATE PROCEDURE — NOT OWNER APPROVED SLA  

---

## 1. Overview & Policy Posture

This playbook outlines the routine procedure for testing Microsoft SQL Server database backups and verifying recovery capabilities.

### Governance Law & Status:
* Candidate targets remain strictly:
  * **Candidate RPO:** $\le 1\text{ hour}$ (`PROPOSED — NOT OWNER APPROVED`)
  * **Candidate RTO:** $\le 4\text{ hours}$ (`PROPOSED — NOT OWNER APPROVED`)
* No binding contractual SLAs or compliance guarantees are ratified until Project Owner review and approval.

---

## 2. Monthly Verification Drill Procedure

### Drill Step 1: Execute Native Compressed Backup
Create an isolated backup archive of the active database:
```sql
BACKUP DATABASE [StudioWebsiteStag]
TO DISK = '/var/backups/mssql/StudioWebsiteStag_drill.bak'
WITH FORMAT, COMPRESSION, STATS = 10,
NAME = 'StudioWebsite-Monthly-Drill';
```

### Drill Step 2: Validate Archive File Structure
Execute `RESTORE VERIFYONLY` to confirm header and checksum integrity:
```sql
RESTORE VERIFYONLY
FROM DISK = '/var/backups/mssql/StudioWebsiteStag_drill.bak';
```
*Expected Output:* `The backup set on file 1 is valid.`

### Drill Step 3: Restore to Dedicated Validation Database
Restore the backup file into an isolated drill database (`StudioWebsiteRestoreDrill`) to test real data restoration without affecting active databases:
```sql
-- Drop previous drill database if present
IF DB_ID('StudioWebsiteRestoreDrill') IS NOT NULL 
    DROP DATABASE [StudioWebsiteRestoreDrill];

RESTORE DATABASE [StudioWebsiteRestoreDrill]
FROM DISK = '/var/backups/mssql/StudioWebsiteStag_drill.bak'
WITH 
    MOVE 'StudioWebsite' TO '/var/opt/mssql/data/StudioWebsiteRestoreDrill.mdf',
    MOVE 'StudioWebsite_log' TO '/var/opt/mssql/data/StudioWebsiteRestoreDrill_log.ldf',
    RECOVERY, REPLACE;
```

### Drill Step 4: Mathematical Consistency Audit (`DBCC CHECKDB`)
Run a physical and logical integrity check across all allocation units and indexes:
```sql
DBCC CHECKDB('StudioWebsiteRestoreDrill') WITH NO_INFOMSGS, ALL_ERRORMSGS;
```
*Pass Condition:* Zero errors, zero allocation faults, zero orphaned constraints.

### Drill Step 5: Clean Up Drill Artifacts
Once verification is logged in the operational record:
```sql
DROP DATABASE [StudioWebsiteRestoreDrill];
```
Log the drill execution time, backup size, duration, and operator initials in the studio operational audit register.
