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

#Insertar usuarios en la bd (Registro)
@app.post("/usuarios/crear")
async def crear_usuario(nombre: str, email: str, contraseña: str):
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute(""" INSERT INTO usuarios (nombre, email, contraseña, fecha_registro) 
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP) 
        ON CONFLICT (email) DO NOTHING 
        RETURNING id_usuario;""", (nombre, email, contraseña))
        usuario = cursor.fetchone()
        conec.commit()
        conec.close()

        if usuario:
            return {"message": "Usuario creado exitosamente", "id_usuario": usuario[0]}
        else:
            raise HTTPException(status_code=400, detail="Email ya existe")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")

#Insertar plantillas (Registro de plantillas mediante administrador)
@app.post("/plantillas")
async def crear_plantilla(nombre: str, descripcion: str, ruta_archivo: str, pagina_firma: int, coord_x: int, coord_y: int):
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute("INSERT INTO plantillas_documento (nombre, descripcion, ruta_archivo, pagina_firma, coord_x, coord_y) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_plantilla;", (nombre, descripcion, ruta_archivo, pagina_firma, coord_x, coord_y))
        plantillan = cursor.fetchone()
        conec.commit()
        conec.close()

        if plantillan:
            return {"message": "Plantilla creada exitosamente", "id_plantilla": plantillan[0]}
        else:
            raise HTTPException(status_code=400, detail="Error al crear plantilla")
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")

#Obtener una plantilla para firmarla (Consulta de plantilla)
@app.get("/plantillas/{id_plantilla}")
async def obtener_plantilla(id_plantilla: int):
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute("SELECT id_plantilla, nombre, descripcion, ruta_archivo, pagina_firma, coord_x, coord_y FROM plantillas_documento WHERE id_plantilla = %s;", (id_plantilla,))
        plantilla = cursor.fetchone()
        conec.close()
        if plantilla:
            return {"id_plantilla": plantilla[0], "nombre": plantilla[1], "descripcion": plantilla[2], "ruta_archivo": plantilla[3], "pagina_firma": plantilla[4], "coord_x": plantilla[5], "coord_y": plantilla[6]}
        else:
            raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")

#Listar todas las plantillas (ver los documentos disponibles para firmar)
@app.get("/plantillas")
async def listar_plantillas():
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute("SELECT * FROM plantillas_documento;")
        plantillas = cursor.fetchall()
        conec.close()
        return [{"id_plantilla": row[0], "nombre": row[1], "descripcion": row[2], "ruta_archivo": row[3], "pagina_firma": row[4]} for row in plantillas]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")

@app.post("/documentos")
async def crear_documento(id_plantilla: int, ruta_pdf: str, estado: str = "pendiente"):
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute("INSERT INTO documentos (id_plantilla, ruta_pdf, ruta_pdf_firmado, fecha_creacion, estado) VALUES (%s, %s, NULL, CURRENT_TIMESTAMP, %s) RETURNING id_documento;", (id_plantilla, ruta_pdf, estado))
        docu = cursor.fetchone()
        conec.commit()
        conec.close()
        if docu:
            return {"message": "Documento creado exitosamente", "id_documento": docu[0]}
        else:
            raise HTTPException(status_code=400, detail="Plantilla no válida")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")


@app.get("/documentos/{id_documento}")
async def obtener_documento(id_documento: int):
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute("SELECT id_documento, id_plantilla, ruta_pdf, ruta_pdf_firmado, fecha_creacion, estado FROM documentos WHERE id_documento = %s;", (id_documento,))
        documento = cursor.fetchone()
        conec.close()
        if documento:
            return {"id_documento": documento[0], "id_plantilla": documento[1], "ruta_pdf": documento[2], "ruta_pdf_firmado": documento[3], "fecha_creacion": documento[4], "estado": documento[5]}
        else:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")


@app.get("/documentos")
async def listar_documentos():
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute("SELECT id_documento, id_plantilla, ruta_pdf, ruta_pdf_firmado, fecha_creacion, estado FROM documentos;")
        documentos = cursor.fetchall()
        conec.close()
        return [{"id_documento": row[0], "id_plantilla": row[1], "ruta_pdf": row[2], "ruta_pdf_firmado": row[3], "fecha_creacion": row[4], "estado": row[5]} for row in documentos]       
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")


@app.post("/logs")
async def crear_log(id_usuario: int, accion: str, detalles: str = None):
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute("INSERT INTO logs (id_usuario, accion, fecha, detalles) VALUES (%s, %s, CURRENT_TIMESTAMP, %s) RETURNING id_log;", (id_usuario, accion, detalles))
        log = cursor.fetchone()
        conec.commit()
        conec.close()
        if log:
            return {"message": "Log creado exitosamente", "id_log": log[0]}
        else:
            raise HTTPException(status_code=400, detail="Usuario no válido")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")


@app.get("/logs")
async def listar_logs():
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute("SELECT id_log, id_usuario, accion, fecha, detalles FROM logs;")
        logs = cursor.fetchall()
        conec.close()
        return [{"id_log": row[0], "id_usuario": row[1], "accion": row[2], "fecha": row[3], "detalles": row[4]} for row in logs] 
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")


#Insertar documentos firmados (Firma exitosa de un docummento)
@app.post("/firmas")
async def crear_firma(id_usuario: int, id_plantilla: int, ruta_firma_img: str, ruta_pdf_firmado: str):
    try:
        conec = conexion()
        cursor = conec.cursor()
        cursor.execute("""
        INSERT INTO firmas (id_usuario, id_plantilla, ruta_firma_img, ruta_pdf_firmado, fecha) 
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) 
        RETURNING id_firma;
        """, (id_usuario, id_plantilla, ruta_firma_img, ruta_pdf_firmado))
        firma = cursor.fetchone()
        conec.commit()
        conec.close()

        if firma:
            return {"message": "Firma creada exitosamente", "id_firma": firma[0]}
        else:
            raise HTTPException(status_code=400, detail="Usuario o plantilla no válidos")

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")


