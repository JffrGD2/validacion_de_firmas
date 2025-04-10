import psycopg2

# Clever Cloud
def conexion():
    return psycopg2.connect(
        host='bmitq7veu7zaz6phfgs2-postgresql.services.clever-cloud.com', 
        port='50013', 
        dbname='bmitq7veu7zaz6phfgs2', 
        user='u8jgl5ydg8hrcjko06ue', 
        password='NFiQcSh7A9JohM2unEe7tD4kbOTJUo', 
        sslmode='require'
    )

try:
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuario ;") 
    users = cursor.fetchall()
    for u in users:
        print(u)
    conn.close()
except Exception as e:
    print("No se pudo conectar")
    print("Error:", e)
