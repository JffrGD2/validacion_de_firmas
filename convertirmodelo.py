from keras.models import load_model
import tensorflow as tf

modelo = load_model('firmodelo.h5')

conversion = tf.lite.TFLiteConverter.from_keras_model(modelo)
conversion.allow_custom_ops = True  
modelite = conversion.convert()

with open('modelfirm.tflite', 'wb') as archivo:
    archivo.write(modelite)

print("¡Modelo convertido exitosamente a TFLite!")
