"""
Spike: Test available ODBC drivers and test connection to potential local SQL Server instances.
"""
import pyodbc
import sys

print(f"Python version: {sys.version}")
print(f"pyodbc version: {pyodbc.version}")
print("Installed ODBC Drivers reported by pyodbc:")
drivers = pyodbc.drivers()
for d in drivers:
    print(f"  - {d}")

# Test connection attempts against standard local SQL Server targets
targets = [
    "Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=master;Trusted_Connection=yes;TrustServerCertificate=yes;",
    "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;Trusted_Connection=yes;TrustServerCertificate=yes;",
    "Driver={SQL Server};Server=localhost;Database=master;Trusted_Connection=yes;",
    "Driver={SQL Server};Server=.\\SQLEXPRESS;Database=master;Trusted_Connection=yes;",
    "Driver={SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=master;Trusted_Connection=yes;",
]

print("\nTesting connection attempts to potential local SQL Server endpoints:")
for conn_str in targets:
    driver_name = conn_str.split(";")[0]
    server_name = conn_str.split(";")[1]
    print(f"\nAttempting: {driver_name}; {server_name}")
    try:
        conn = pyodbc.connect(conn_str, timeout=3)
        print(f"  --> SUCCESS: Connected!")
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION AS version, DB_NAME() AS current_db")
        row = cursor.fetchone()
        print(f"  --> SQL Server Version: {row[0]}")
        print(f"  --> Current Database: {row[1]}")
        conn.close()
    except Exception as e:
        print(f"  --> FAILED: {type(e).__name__}: {e}")
