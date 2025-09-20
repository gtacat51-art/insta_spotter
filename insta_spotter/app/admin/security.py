import os
import secrets
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

# --- Configurazione di Sicurezza ---
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # Scade dopo 24 ore

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")

# --- Funzioni di Utility JWT (JSON Web Token) ---

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    """In un'app reale, qui useresti una libreria come passlib per confrontare hash.
    Per questo progetto, confrontiamo la password in chiaro per semplicità.
    """
    return secrets.compare_digest(plain_password, hashed_password)

# --- Logica di Autenticazione ---

def authenticate_user(username: str, password: str):
    """Verifica se l'utente esiste e la password è corretta."""
    if username == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD):
        return username
    return None

def get_current_user(request: Request):
    """Dipendenza per ottenere l'utente corrente dal token nel cookie."""
    token = request.cookies.get("access_token")
    if not token:
        return None # Nessun utente loggato

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    return username