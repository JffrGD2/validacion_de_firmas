import matplotlib.pyplot as plt
from preprocesamiento import imagenes_train, etiquetas_train, imagenes_test

# Mostrar una imagen de ejemplo con su etiqueta
if len(imagenes_train) > 0:
    img = imagenes_train[7]
    plt.imshow(img, cmap='gray')
    plt.title("Etiqueta de esta imagen: " + str(etiquetas_train[7]))
    plt.show()
else:
    print("No hay imágenes de entrenamiento cargadas.")

# Paraa confirmar tamaño de las imágenes cargadas
if imagenes_train.size > 0:
    print(f"Dimensión de entrenamiento: {imagenes_train[0].shape}")
if imagenes_test.size > 0:
    print(f"Dimensión de prueba: {imagenes_test[0].shape}")
