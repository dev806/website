"""
Spike SP-04: SQLAlchemy 2.0 MSSQL Dialect and Alembic DDL Generation
Verifies that SQLAlchemy models compile to valid Microsoft SQL Server T-SQL,
and tests Alembic migration operation emission under mssql dialect.
"""
import io
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects import mssql
from alembic.migration import MigrationContext
from alembic.operations import Operations
from spikes.models_spike import Base, DiscoverySessionSpike, ProblemSubmissionSpike, AuditLogSpike

print("=" * 70)
print("SP-04: SQLALCHEMY MSSQL DIALECT & ALEMBIC DDL TEST")
print("=" * 70)

dialect = mssql.dialect()

# 1. Compile SQLAlchemy Models to MSSQL DDL
print("\n[1] Compiling Declarative Models to MSSQL T-SQL:")
tables = [DiscoverySessionSpike.__table__, ProblemSubmissionSpike.__table__, AuditLogSpike.__table__]

compiled_sqls = []
for table in tables:
    create_stmt = CreateTable(table).compile(dialect=dialect)
    sql_str = str(create_stmt).strip()
    compiled_sqls.append(sql_str)
    print(f"\n--- DDL for {table.name} ---")
    print(sql_str)
    for idx in table.indexes:
        idx_stmt = CreateIndex(idx).compile(dialect=dialect)
        print(f"--- Index DDL: {idx.name} ---")
        print(str(idx_stmt).strip())

# Verify MSSQL-specific types and keywords in compiled output
all_ddl = "\n".join(compiled_sqls)
assert "UNIQUEIDENTIFIER" in all_ddl, "Expected UNIQUEIDENTIFIER in T-SQL DDL"
assert "DATETIME2" in all_ddl, "Expected DATETIME2 in T-SQL DDL"
assert "CONSTRAINT chk_problem_min_length CHECK" in all_ddl, "Expected CHECK constraint in T-SQL DDL"
assert "FOREIGN KEY(session_id) REFERENCES discovery_sessions (id)" in all_ddl, "Expected FK with REFERENCES"
print("\n[PASS] SQLAlchemy models compile to standard MSSQL T-SQL with correct dialect types.")

# 2. Test Alembic Migration Operations with MSSQL Dialect
print("\n[2] Testing Alembic Operations emission in MSSQL offline mode:")
buf = io.StringIO()
ctx = MigrationContext.configure(
    dialect=dialect,
    opts={"as_sql": True, "output_buffer": buf}
)
op = Operations(ctx)

from sqlalchemy import Column

# Simulate Alembic upgrade migration operations
op.create_table(
    "spike_test_table",
    Column("id", mssql.UNIQUEIDENTIFIER(), primary_key=True),
    Column("name", mssql.NVARCHAR(100), nullable=False)
)
op.add_column("spike_test_table", Column("notes", mssql.NVARCHAR(500)))
op.create_index("ix_spike_notes", "spike_test_table", ["notes"])
op.drop_table("spike_test_table")

alembic_sql = buf.getvalue()
print("\nAlembic Generated T-SQL:")
print(alembic_sql.strip())

assert "CREATE TABLE spike_test_table" in alembic_sql, "Alembic should emit CREATE TABLE"
assert "ALTER TABLE spike_test_table ADD notes NVARCHAR(500)" in alembic_sql or "ADD notes" in alembic_sql
assert "DROP TABLE spike_test_table" in alembic_sql

print("\n[PASS] Alembic Operations successfully emit valid T-SQL for MSSQL.")
print("=" * 70)
