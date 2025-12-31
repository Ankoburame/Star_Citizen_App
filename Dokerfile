FROM python:3.11-slim

WORKDIR /app

# Copier requirements
COPY backend/requirements.txt .

# Installer dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code backend
COPY backend/ .

# Exposer le port
EXPOSE 8000

# Lancer l'app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### **ÉTAPE 5 : Sauvegarder le fichier**

**Ctrl+S ou Fichier → Enregistrer**

---

### **ÉTAPE 6 : Vérifier où il est**

**Ta structure doit être :**
```
STAR_CITIZEN_APP/
├── Dockerfile          ← ICI ! Le nouveau !
├── backend/
│   ├── main.py
│   └── requirements.txt
└── frontend/