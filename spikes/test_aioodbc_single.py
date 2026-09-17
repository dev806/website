import asyncio
import time
import aioodbc

async def main():
    print("Testing aioodbc connection...")
    conn_str = "Driver={ODBC Driver 18 for SQL Server};Server=.\\SQLEXPRESS;Database=StudioWebsiteDev;Trusted_Connection=yes;TrustServerCertificate=yes;"
    t_conn = time.perf_counter()
    conn = await aioodbc.connect(dsn=conn_str)
    print(f"aioodbc connected in {(time.perf_counter()-t_conn)*1000:.2f} ms")
    
    t0 = time.perf_counter()
    cursor = await conn.cursor()
    await cursor.execute("SELECT 1")
    row = await cursor.fetchone()
    print(f"aioodbc query returned {row[0]} in {(time.perf_counter()-t0)*1000:.2f} ms")
    
    await cursor.close()
    await conn.close()
    print("aioodbc closed cleanly")

if __name__ == "__main__":
    asyncio.run(main())
