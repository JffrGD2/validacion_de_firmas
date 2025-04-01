{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": []
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "code",
      "source": [
        "#!pip install tensorflow opencv-python numpy matplotlib scikit-learn seaborn scikit-image flask keras fastapi uvicorn sqlalchemy\n",
        "\n",
        "\n",
        "import tensorflow as tf\n",
        "import cv2\n",
        "import numpy as np\n",
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "import sklearn\n",
        "from skimage import io, color, filters, feature"
      ],
      "metadata": {
        "id": "NZXcaZ1lSLi7"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "import sqlite3\n",
        "import numpy as np\n",
        "from sklearn.model_selection import train_test_split\n",
        "\n",
        "conn = sqlite3.connect('/content/BDFirmas.db')\n",
        "cursor = conn.cursor()\n",
        "print(\"Conexión exitosa a la base de datos\")\n",
        "\n",
        "\n",
        "cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")\n",
        "tablas = cursor.fetchall()\n",
        "print(\"tablas =\", [tabla[0] for tabla in tablas])\n",
        "\n",
        "\n",
        "conn.close()"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "8vIu0PyaTdRo",
        "outputId": "3291804b-a9f3-4dba-8bfc-08bbcbb52b9c"
      },
      "execution_count": null,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Conexión exitosa a la base de datos\n",
            "tablas = ['sqlite_sequence', 'firma', 'documento', 'usuario', 'firmas_usuarios', 'comparacion_firmas', 'registro_fraudes', 'tipos_documentos', 'parametros_sistema', 'historial_firmas', 'logs_actividad', 'dispositivos_registrados', 'intentos_firma']\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "from google.colab import drive\n",
        "drive.mount('/content/drive')\n",
        "\n",
        "dataset_path = \"/content/drive/MyDrive/Colab Notebooks/processed_images_train\"\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "pY0XrkerJB61",
        "outputId": "a010dd56-6dbb-40fa-8c42-3fa297361cda"
      },
      "execution_count": null,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Drive already mounted at /content/drive; to attempt to forcibly remount, call drive.mount(\"/content/drive\", force_remount=True).\n"
          ]
        }
      ]
    },
    {
      "cell_type": "markdown",
      "source": [
        "# Sección nueva"
      ],
      "metadata": {
        "id": "7ANNRUmNoHY6"
      }
    },
    {
      "cell_type": "code",
      "source": [
        "from google.colab import drive\n",
        "import os\n",
        "import cv2\n",
        "import numpy as np\n",
        "\n",
        "train = '/content/drive/MyDrive/Colab Notebooks/Processed_Images_Train'\n",
        "test = '/content/drive/MyDrive/Colab Notebooks/Processed_Images_Test'\n",
        "\n",
        "def preprocesar_imagenes(directorio, tamaño=(128, 128)):\n",
        "    imagenes_procesadas = []\n",
        "    etiquetas = []\n",
        "\n",
        "    if not os.path.exists(directorio):\n",
        "        print(f\"Error: El directorio '{directorio}' no existe.\")\n",
        "        return np.array([]), np.array([])\n",
        "\n",
        "    for etiqueta in os.listdir(directorio):\n",
        "        carpeta = os.path.join(directorio, etiqueta)\n",
        "\n",
        "        if not os.path.isdir(carpeta):\n",
        "            continue\n",
        "\n",
        "        for nombre_imagen in os.listdir(carpeta):\n",
        "            ruta_imagen = os.path.join(carpeta, nombre_imagen)\n",
        "\n",
        "            imagen = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)\n",
        "            if imagen is None:\n",
        "                print(f\"Advertencia: No se pudo cargar '{ruta_imagen}', se omitirá.\")\n",
        "                continue\n",
        "\n",
        "\n",
        "            imagen = cv2.resize(imagen, tamaño)\n",
        "            imagen = imagen.astype(np.float32) / 255.0\n",
        "\n",
        "            # datos\n",
        "            imagenes_procesadas.append(imagen)\n",
        "            etiquetas.append(etiqueta)\n",
        "\n",
        "    if not imagenes_procesadas:\n",
        "        print(\"Error: No se encontraron imágenes válidas.\")\n",
        "        return np.array([]), np.array([])\n",
        "\n",
        "    return np.array(imagenes_procesadas), np.array(etiquetas)\n",
        "\n",
        "# Preprocesar las imágenes de entrenamiento y prueba\n",
        "imagenes_train, etiquetas_train = preprocesar_imagenes(train)\n",
        "imagenes_test, etiquetas_test = preprocesar_imagenes(test)\n",
        "\n",
        "print(f\"Total imágenes de entrenamiento: {len(imagenes_train)}\")\n",
        "print(f\"Total imágenes de prueba: {len(imagenes_test)}\")\n",
        "\n",
        "if imagenes_train.size > 0:\n",
        "    print(f\"Dimensión de entrenamiento: {imagenes_train[0].shape}\")\n",
        "if imagenes_test.size > 0:\n",
        "    print(f\"Dimensión de prueba: {imagenes_test[0].shape}\")\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "-PCuOJnywWmk",
        "outputId": "c6ff1b6a-7912-46df-cfb7-4dbb605a59a8"
      },
      "execution_count": 43,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Total imágenes de entrenamiento: 186\n",
            "Total imágenes de prueba: 184\n",
            "Dimensión de entrenamiento: (128, 128)\n",
            "Dimensión de prueba: (128, 128)\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "import matplotlib.pyplot as plt # immportamos esto para mostrar graficas\n",
        "\n",
        "img = imagenes_train[7]\n",
        "plt.imshow(img, cmap='gray')\n",
        "plt.title(\"Etiqueta de esta imagen: \" + str(etiquetas_train[0]))  # para blanco y negr0\n",
        "plt.show()  # a ver qué sale ☠"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/",
          "height": 452
        },
        "id": "v3pA4Ip9qAli",
        "outputId": "bc16360a-99dc-4e7a-dc5b-319f9175f6f0"
      },
      "execution_count": 59,
      "outputs": [
        {
          "output_type": "display_data",
          "data": {
            "text/plain": [
              "<Figure size 640x480 with 1 Axes>"
            ],
            "image/png": "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\n"
          },
          "metadata": {}
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "# confirmamos el tamaño de las imagenes que estén del mismo tamaño\n",
        "if imagenes_train.size > 0:\n",
        "    print(f\"Dimensión de entrenamiento: {imagenes_train[0].shape}\")\n",
        "if imagenes_test.size > 0:\n",
        "    print(f\"Dimensión de prueba: {imagenes_test[0].shape}\")\n"
      ],
      "metadata": {
        "id": "psTo8huxH6yL",
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "outputId": "d7aa4ef5-e62f-422d-d055-64f4c5aaebbd"
      },
      "execution_count": 54,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Dimensión de entrenamiento: (128, 128)\n",
            "Dimensión de prueba: (128, 128)\n"
          ]
        }
      ]
    }
  ]
}
