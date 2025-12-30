from database import engine, Base
import models  # ⚠️ important : force l'import des modèles

print("Création des tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès")
