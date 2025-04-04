import fastapi 
import sqlite3

conn = sqlite3.connect('/content/BDFirmas.db')
cursor = conn.cursor()
print("Conexión exitosa a la base de datos")
 
 
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()
print("tablas =", [tabla[0] for tabla in tablas])
 
 
conn.close()