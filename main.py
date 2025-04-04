from fastapi import FastAPI, HTTPException
import logging
from fastapi.middleware.gzip import GZipMiddleware
import sqlite3

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a la API de BDFirmas"}

def conectar():
    return sqlite3.connect("BDFirmas.db")

@app.get("/tablas")
def tablas():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    conexion.close()
    if not tablas:
        raise HTTPException(status_code=404, detail="No hay tablas en la base de datos")
    else:
        return [{"tablas": tabla[0]} for tabla in tablas]
