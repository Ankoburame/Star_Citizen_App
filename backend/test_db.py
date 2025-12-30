from database import engine

try:
    conn = engine.connect()
    print("✅ Connexion PostgreSQL OK")
    conn.close()
except Exception as e:
    print("❌ Erreur DB :", e)
