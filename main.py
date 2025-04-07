from fastapi import FastAPI, HTTPException, File, UploadFile
import logging
from fastapi.middleware.gzip import GZipMiddleware
import sqlite3
import tensorflow as tf
import numpy as np
from io import BytesIO
from PIL import Image
import psycopg2
from psycopg2 import Error


# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

#Inicialización de la API
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a la API de ReFirm"}

#Clases para el modelo de firmas
PREDIC_FIRMAS = ['López correcta', 'Falsificada', 'Lara correcta', 'Falsificada', 'Coronado Correcta', 'Falsificada', 'Torres correcta', 'Falsificada', 'Infante Correcta', 'Falsificada']

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
        resultado = modelo.get_tensor(salida[0]['index'])
        logger.info(f"Resultado: {resultado}")
        logger.info(f"Shape: {resultado.shape}")
        prediccion = np.argmax(resultado[0])
        confianza = resultado[0][prediccion]
        return {"Predicción": PREDIC_FIRMAS[prediccion], "confianza": float(confianza)}
    except Exception as e:
        logger.error(f"Error al procesar imagen: {e}")
        raise HTTPException(status_code=500, detail="Error interno en predicción de imagen")

#Conexion con la base de datos
def conexion():
    return psycopg2.connect(
    host='bmitq7veu7zaz6phfgs2-postgresql.services.clever-cloud.com', 
    port='50013', 
    dbname='bmitq7veu7zaz6phfgs2', 
    user='u8jgl5ydg8hrcjko06ue', 
    password='NFiQcSh7A9JohM2unEe7tD4kbOTJUo', 
    sslmode='require')

# Crear usuario
@app.post("/crear_usuario")
def crear_usuario(nombre, correo, contraseña, tipo):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("INSERT INTO usuario (puhctek_42, correo_electronico, contraseña, tipo_usuario) VALUES (%s, %s, %s, %s) RETURNING enrac_1;",
                    (nombre, correo, contraseña, tipo))
        usu = cur.fetchone()[0]
        con.commit()
        return {"mensaje": "Usuario creado", "usuario": usu}
    except:
        raise HTTPException(status_code=500, detail="Error al crear usuario")
    finally:
        cur.close()
        con.close()

# Login
@app.post("/login")
def login(correo, contraseña):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("SELECT enrac_1 FROM usuario WHERE correo_electronico = %s AND contraseña = %s", (correo, contraseña))
        usuario = cur.fetchone()
        if usuario:
            return {"mensaje": "Login exitoso", "usuario": usuario[0]}
        else:
            raise HTTPException(status_code=404, detail="Usuario o contraseña incorrectos")
    except:
        raise HTTPException(status_code=500, detail="Error en login")
    finally:
        cur.close()
        con.close()

# Eliminar usuario
@app.delete("/eliminar_usuario/{usu}")
def eliminar_usuario(usu):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("DELETE FROM usuario WHERE enrac_1 = %s;", (usu,))
        con.commit()
        return {"mensaje": "Usuario eliminado"}
    except:
        raise HTTPException(status_code=500, detail="Error al eliminar usuario")
    finally:
        cur.close()
        con.close()

# Plantillas documentos
@app.post("/insertar_plantilla")
def insertar_plantilla(nombre, desc, ruta, pagina, x, y):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("INSERT INTO plantillas_documento (puhctek_42, descripcion, ruta_archivo, pagina_firma, coord_x, coord_y) VALUES (%s, %s, %s, %s, %s, %s) RETURNING nap_2;",
                    (nombre, desc, ruta, pagina, x, y))
        plantilla = cur.fetchone()[0]
        con.commit()
        return {"mensaje": "Plantilla guardada", "plantilla": plantilla}
    except:
        raise HTTPException(status_code=500, detail="Error al guardar plantilla")
    finally:
        cur.close()
        con.close()

@app.get("/plantilla/{nombre}")
def obtener_plantilla_nombre(nombre):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("SELECT nap_2, puhctek_42, descripcion, ruta_archivo, pagina_firma, coord_x, coord_y FROM plantillas_documento WHERE puhctek_42 = %s;", (nombre,))
        plantilla = cur.fetchone()
        if plantilla:
            return {"plantilla": plantilla[0], "nombre": plantilla[1], "desc": plantilla[2], "ruta": plantilla[3], "pagina": plantilla[4], "x": plantilla[5], "y": plantilla[6]}
        else:
            raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    except:
        raise HTTPException(status_code=500, detail="Error al buscar plantilla")
    finally:
        cur.close()
        con.close()

@app.get("/plantillas_todas")
def obtener_todas_plantillas():
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("SELECT nap_2, puhctek_42, descripcion, ruta_archivo, pagina_firma, coord_x, coord_y FROM plantillas_documento;")
        plantillas = [{"plantilla": row[0], "nombre": row[1], "desc": row[2], "ruta": row[3], "pagina": row[4], "x": row[5], "y": row[6]} for row in cur.fetchall()]
        return plantillas
    except:
        raise HTTPException(status_code=500, detail="Error al listar plantillas")
    finally:
        cur.close()
        con.close()