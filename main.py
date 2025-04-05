from fastapi import FastAPI, HTTPException, File, UploadFile
import logging
from fastapi.middleware.gzip import GZipMiddleware
import sqlite3
import tensorflow as tf
import numpy as np
from io import BytesIO
from PIL import Image

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

#Inicialización de la API
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

#Clases para el modelo de firmas
PREDIC_FIRMAS = ['Firma válida', 'Firma Falsa']

#Cargar el modelo de imágenes
modelo = tf.lite.Interpreter(model_path="modelfirm.tflite")
modelo.allocate_tensors()
entrada = modelo.get_input_details()
salida = modelo.get_output_details()
forma = entrada[0]['shape']

#Petición para subir imagen
@app.post("/predict/image/")
async def predict_image(archivo: UploadFile = File(...)):
    if not archivo.filename.lower().endswith(("jpg", "jpeg", "png")):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen en formato JPG o PNG")
    try:
        img = await archivo.read()
        imagen = Image.open(BytesIO(img)).convert("RGB")
        imagen = imagen.resize((forma[1], forma[2]))
        img_arr = np.array(imagen) / 255.0
        img_arr = np.expand_dims(img_arr, axis=0).astype(np.float32)
        modelo.set_tensor(entrada[0]['index'], img_arr)
        modelo.invoke()
        salida = modelo.get_tensor(salida[0]['index'])
        prediccion = np.argmax(salida)
        confianza = salida[prediccion]
        return {"Predicción": PREDIC_FIRMAS[prediccion], "confianza": float(confianza)}
    except Exception as e:
        logger.error(f"Error al procesar imagen: {e}")
        raise HTTPException(status_code=500, detail="Error interno en predicción de imagen")
    finally:
        img.close()


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


