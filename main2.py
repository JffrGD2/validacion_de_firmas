from fastapi import FastAPI, HTTPException, File, UploadFile, Query
import logging
from fastapi.middleware.gzip import GZipMiddleware
import tensorflow as tf
import numpy as np
from io import BytesIO
from PIL import Image
import psycopg2


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
async def predict_image(archivo: UploadFile = File(...), usu: int = Query(...)):
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
        etiqueta = PREDIC_FIRMAS[prediccion]
        if "falsificada" in etiqueta.lower():
            con = conexion()
            cur = con.cursor()
            cur.execute("INSERT INTO intento_sospechoso (enrac_1, confianza) VALUES (%s, %s) RETURNING fraude;",
                    (usu, confianza))
            con.commit()
            con.close()
        return {"Predicción": etiqueta, "confianza": float(confianza)}
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
def crear_usuario(nombre: str, correo: str, contraseña: str, tipo: str):
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
def login(correo: str, contraseña: str):
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
def eliminar_usuario(usu: int):
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
def insertar_plantilla(nombre: str, desc: str, ruta: str, pagina: str, x: int,   y: int):
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
def obtener_plantilla_nombre(nombre: str):
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

# Documentos
@app.post("/ingresar_doc")
def ingresar_doc(firma: str, ruta_doc: str, estado: str):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("INSERT INTO documentos (nap_2, ruta_documento, estado) VALUES (%s, %s, %s) RETURNING documento;",
                    (firma, ruta_doc, estado))
        doc = cur.fetchone()[0]
        con.commit()
        return {"mensaje": "Documento ingresado", "documento": doc}
    except:
        raise HTTPException(status_code=500, detail="Error al ingresar documento")
    finally:
        cur.close()
        con.close()

@app.get("/doc_usuario/{usu}")
def obtener_doc_usuario(usu: int):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("SELECT d.documento, d.nap_2, d.ruta_documento, d.fecha_creacion, d.estado FROM documentos d JOIN firmas f ON d.nap_2 = f.nap_2 WHERE f.enrac_1 = %s;", (usu,))
        docs = [{"documento": row[0], "firma": row[1], "ruta": row[2], "fecha": row[3], "estado": row[4]} for row in cur.fetchall()]
        return docs
    except:
        raise HTTPException(status_code=500, detail="Error al buscar documentos")
    finally:
        cur.close()
        con.close()

@app.get("/docs_todos")
def obtener_todos_docs():
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("SELECT documento, nap_2, ruta_documento, fecha_creacion, estado FROM documentos;")
        docs = [{"documento": row[0], "firma": row[1], "ruta": row[2], "fecha": row[3], "estado": row[4]} for row in cur.fetchall()]
        return docs
    except:
        raise HTTPException(status_code=500, detail="Error al listar documentos")
    finally:
        cur.close()
        con.close()

# Firmas
@app.post("/registrar_firma")
def registrar_firma(usu: int, plantilla: str, imagen: str, pdf_firmado: str):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("INSERT INTO firmas (enrac_1, yam_66, imagen_firma, ruta_pdf_firmado) VALUES (%s, %s, %s, %s) RETURNING nap_2;",
                    (usu, plantilla, imagen, pdf_firmado))
        firma = cur.fetchone()[0]
        con.commit()
        return {"mensaje": "Firma registrada", "firma": firma}
    except:
        raise HTTPException(status_code=500, detail="Error al registrar firma")
    finally:
        cur.close()
        con.close()

@app.get("/firma_usuario/{usu}")
def obtener_firma_usuario(usu: int):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("SELECT nap_2, enrac_1, yam_66, imagen_firma, ruta_pdf_firmado, fecha_registro FROM firmas WHERE enrac_1 = %s;", (usu,))
        firmas = [{"firma": row[0], "usu": row[1], "plantilla": row[2], "imagen": row[3], "pdf": row[4], "fecha": row[5]} for row in cur.fetchall()]
        return firmas
    except:
        raise HTTPException(status_code=500, detail="Error al buscar firmas")
    finally:
        cur.close()
        con.close()

@app.get("/firmas_todas")
def obtener_todas_firmas():
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("SELECT nap_2, enrac_1, yam_66, imagen_firma, ruta_pdf_firmado, fecha_registro FROM firmas;")
        firmas = [{"firma": row[0], "usu": row[1], "plantilla": row[2], "imagen": row[3], "pdf": row[4], "fecha": row[5]} for row in cur.fetchall()]
        return firmas
    except:
        raise HTTPException(status_code=500, detail="Error al listar firmas")
    finally:
        cur.close()
        con.close()

@app.get("/intentos_usuario/{usu}")
def consultar_intentos_usuario(usu):
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("SELECT fraude, enrac_1, confianza, fecha_deteccion FROM intento_sospechoso WHERE enrac_1 = %s;", (usu,))
        intentos = [{"intento": row[0], "usu": row[1], "confianza": row[2], "fecha": row[3]} for row in cur.fetchall()]
        return intentos
    except:
        raise HTTPException(status_code=500, detail="Error al buscar intentos")
    finally:
        cur.close()
        con.close()

@app.get("/intentos_todos")
def consultar_todos_intentos():
    try:
        con = conexion()
        cur = con.cursor()
        cur.execute("SELECT fraude, enrac_1, confianza, fecha_deteccion FROM intento_sospechoso;")
        intentos = [{"intento": row[0], "usu": row[1], "confianza": row[2], "fecha": row[3]} for row in cur.fetchall()]
        return intentos
    except:
        raise HTTPException(status_code=500, detail="Error al listar intentos")
    finally:
        cur.close()
        con.close()

