from fastapi import FastAPI
from app.database import create_db_and_tables
from app.web import routes as web_routes
from app.admin import routes as admin_routes

# --- Creazione dell'Applicazione ---

app = FastAPI(
    title="InstaSpotter",
    description="Bot per la pubblicazione di messaggi spotted anonimi su Instagram Stories.",
    version="1.0.0"
)

# --- Eventi di Avvio e Spegnimento ---

@app.on_event("startup")
def on_startup():
    """Funzioni da eseguire all'avvio dell'applicazione."""
    print("Avvio dell'applicazione InstaSpotter...")
    # Crea le tabelle del database se non esistono
    create_db_and_tables()
    print("Database e tabelle pronti.")

# --- Inclusione delle Rotte ---

# Includi le rotte definite nel modulo web
app.include_router(web_routes.router)
app.include_router(admin_routes.router)

# --- Rotta di Benvenuto ---

@app.get("/", tags=["Root"])
def read_root():
    """Ritorna un messaggio di benvenuto."""
    return {"message": "Benvenuto in InstaSpotter. Vai su /spotted/new per inviare un messaggio."}
