from google.colab import drive
import os
import cv2
import numpy as np

train = '/content/drive/MyDrive/Colab Notebooks/Processed_Images_Train'
test = '/content/drive/MyDrive/Colab Notebooks/Processed_Images_Test'

def preprocesar_imagenes(directorio, tamaño=(128, 128)):
    imagenes_procesadas = []
    etiquetas = []

    if not os.path.exists(directorio):
        print(f"Error: El directorio '{directorio}' no existe.")
        return np.array([]), np.array([])

    for etiqueta in os.listdir(directorio):
        carpeta = os.path.join(directorio, etiqueta)

        if not os.path.isdir(carpeta):
            continue

        for nombre_imagen in os.listdir(carpeta):
            ruta_imagen = os.path.join(carpeta, nombre_imagen)

            imagen = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
            if imagen is None:
                print(f"Advertencia: No se pudo cargar '{ruta_imagen}', se omitirá.")
                continue


            imagen = cv2.resize(imagen, tamaño)
            imagen = imagen.astype(np.float32) / 255.0

            # datos
            imagenes_procesadas.append(imagen)
            etiquetas.append(etiqueta)

    if not imagenes_procesadas:
        print("Error: No se encontraron imágenes válidas.")
        return np.array([]), np.array([])

    return np.array(imagenes_procesadas), np.array(etiquetas)

# Preprocesar las imágenes de entrenamiento y prueba
imagenes_train, etiquetas_train = preprocesar_imagenes(train)
imagenes_test, etiquetas_test = preprocesar_imagenes(test)

print(f"Total imágenes de entrenamiento: {len(imagenes_train)}")
print(f"Total imágenes de prueba: {len(imagenes_test)}")

if imagenes_train.size > 0:
    print(f"Dimensión de entrenamiento: {imagenes_train[0].shape}")
if imagenes_test.size > 0:
    print(f"Dimensión de prueba: {imagenes_test[0].shape}")
