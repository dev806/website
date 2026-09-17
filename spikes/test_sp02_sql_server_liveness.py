"""
Spike SP-02: Comprehensive SQL Server 2022 + ODBC Driver 18 Liveness Validation
Validates all 10 required database criteria against local Microsoft SQL Server 2022 Express.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))
import pyodbc
from sqlalchemy import create_engine, text

print("=" * 70)
print("SP-02: SQL SERVER 2022 + ODBC DRIVER 18 LIVENESS VALIDATION")
print("=" * 70)

CONN_STR_MASTER = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=.\\SQLEXPRESS;"
    "Database=master;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# Step 1: Connect to master and provision StudioWebsiteDev and StudioWebsiteTest if needed
print("\n[Step 1] Connecting to SQL Server master database via ODBC Driver 18...")
conn_master = pyodbc.connect(CONN_STR_MASTER, autocommit=True)
cursor_master = conn_master.cursor()

# Get server details
cursor_master.execute("SELECT @@SERVERNAME, @@VERSION")
row = cursor_master.fetchone()
print(f"  --> Server Instance: {row[0]}")
print(f"  --> Version: {row[1].splitlines()[0]}")

# Ensure databases exist with RCSI
for db_name in ["StudioWebsiteDev", "StudioWebsiteTest"]:
    cursor_master.execute(f"SELECT database_id, is_read_committed_snapshot_on FROM sys.databases WHERE name = '{db_name}'")
    db_row = cursor_master.fetchone()
    if not db_row:
        print(f"  --> Creating database '{db_name}'...")
        cursor_master.execute(f"CREATE DATABASE {db_name}")
        cursor_master.execute(f"ALTER DATABASE {db_name} SET READ_COMMITTED_SNAPSHOT ON")
        print(f"  --> Created '{db_name}' and enabled READ_COMMITTED_SNAPSHOT.")
    else:
        rcsi_status = "ENABLED" if db_row[1] == 1 else "DISABLED"
        print(f"  --> Database '{db_name}' exists (RCSI: {rcsi_status}).")
        if db_row[1] == 0:
            cursor_master.execute(f"ALTER DATABASE {db_name} SET READ_COMMITTED_SNAPSHOT ON")
            print(f"      Enabled READ_COMMITTED_SNAPSHOT on '{db_name}'.")

conn_master.close()
print("  --> Master connection closed cleanly.")

# Step 2: Validate 10 Specific Criteria against StudioWebsiteDev & StudioWebsiteTest
CONN_STR_DEV = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=.\\SQLEXPRESS;"
    "Database=StudioWebsiteDev;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)
CONN_STR_TEST = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=.\\SQLEXPRESS;"
    "Database=StudioWebsiteTest;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

print("\n[Step 2] Executing 10-Point Validation Checklist:")

# 1. SQL Server reachable
print("  1. SQL Server reachable: PASS (Connected to .\\SQLEXPRESS)")

# 2. Windows Integrated Authentication
print("  2. Windows Integrated Authentication: PASS (Trusted_Connection=yes authenticated)")

# 3. Python can connect through ODBC Driver 18
conn_dev = pyodbc.connect(CONN_STR_DEV)
print("  3. Python ODBC Driver 18 connection: PASS (Successfully connected to StudioWebsiteDev)")

# 4. SQLAlchemy can connect
alchemy_url = (
    "mssql+pyodbc:///?odbc_connect="
    "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
    "Server%3D.%5CSQLEXPRESS%3BDatabase%3DStudioWebsiteDev%3B"
    "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
)
engine = create_engine(alchemy_url)
with engine.connect() as alch_conn:
    res = alch_conn.execute(text("SELECT 42 AS test_val")).fetchone()
    assert res[0] == 42
print("  4. SQLAlchemy 2.0 connection: PASS (mssql+pyodbc engine connected and executed query)")

# 5. Simple query succeeds
cursor = conn_dev.cursor()
cursor.execute("SELECT 1 AS liveness")
assert cursor.fetchone()[0] == 1
print("  5. Simple query succeeds: PASS (SELECT 1 returned 1)")

# Setup temporary table for transaction & parameter testing
cursor.execute("""
    IF OBJECT_ID('dbo.spike_tmp_test', 'U') IS NOT NULL DROP TABLE dbo.spike_tmp_test;
    CREATE TABLE dbo.spike_tmp_test (id INT PRIMARY KEY, val NVARCHAR(100));
""")
conn_dev.commit()

# 6. Transaction commit succeeds
cursor.execute("INSERT INTO dbo.spike_tmp_test (id, val) VALUES (?, ?)", (1, "committed_value"))
conn_dev.commit()
cursor.execute("SELECT val FROM dbo.spike_tmp_test WHERE id = 1")
assert cursor.fetchone()[0] == "committed_value"
print("  6. Transaction commit succeeds: PASS (Row inserted and verified after commit)")

# 7. Transaction rollback succeeds
cursor.execute("INSERT INTO dbo.spike_tmp_test (id, val) VALUES (?, ?)", (2, "rollback_value"))
conn_dev.rollback()
cursor.execute("SELECT val FROM dbo.spike_tmp_test WHERE id = 2")
assert cursor.fetchone() is None
print("  7. Transaction rollback succeeds: PASS (Row rolled back cleanly; query returned None)")

# 8. Parameterized query succeeds (SQL Injection prevention)
param_input = "'; DROP TABLE dbo.spike_tmp_test; --"
cursor.execute("SELECT val FROM dbo.spike_tmp_test WHERE val = ?", (param_input,))
assert cursor.fetchone() is None
cursor.execute("SELECT COUNT(*) FROM dbo.spike_tmp_test")
assert cursor.fetchone()[0] == 1  # Table still exists!
print("  8. Parameterized query succeeds: PASS (Parameterized query successfully isolated SQL payload)")

# Cleanup temp table
cursor.execute("DROP TABLE dbo.spike_tmp_test")
conn_dev.commit()

# 9. Connection closed cleanly
cursor.close()
conn_dev.close()
print("  9. Connection closed cleanly: PASS (Cursor and connection closed without leaks)")

# 10. Test database can be independently accessed
conn_test = pyodbc.connect(CONN_STR_TEST)
cursor_test = conn_test.cursor()
cursor_test.execute("SELECT DB_NAME() AS current_db")
current_test_db = cursor_test.fetchone()[0]
assert current_test_db == "StudioWebsiteTest"
cursor_test.close()
conn_test.close()
print(f" 10. Independent test DB access: PASS (Connected to '{current_test_db}' independently)")

print("\n" + "=" * 70)
print("[VERDICT: SP-02 FULLY VERIFIED — 10/10 CRITERIA PASSED]")
print("=" * 70)
