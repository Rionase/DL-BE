import tensorflow as tf
import os
import numpy as np
from matplotlib import pyplot as plt
import math

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout

from lib.GetLastModel import GetLastModelFile, GetLastModelCount

def getModel () :

    # NO SAVED MODELS FOUND, CREATE NEW MODELS
    if ( GetLastModelFile() == False ) :

        # CREATING CNN MODEL
        model = Sequential()

        model.add(Conv2D(16, (3,3), 1, activation='relu', input_shape=(256,256,3)))
        model.add(MaxPooling2D())
        model.add(Conv2D(32, (3,3), 1, activation='relu'))
        model.add(MaxPooling2D())
        model.add(Conv2D(16, (3,3), 1, activation='relu'))
        model.add(MaxPooling2D())
        model.add(Flatten())
        model.add(Dense(256, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))

        model.compile('adam', loss=tf.losses.BinaryCrossentropy(), metrics=['accuracy'])
        return model
        
    else :
        model = load_model(f"models/{GetLastModelFile()}")
        model.compile('adam', loss=tf.losses.BinaryCrossentropy(), metrics=['accuracy'])
        return model


def ModelingAndTrain () :
    # GENERATE AND PREPOCESSING DATASET 
    # MAKE EACH DATASET INTO 256 X 256 ( DEFAULT FROM FUNCTION )
    # MAKE IT INTO BATCH WITH EACH BATCH IS 32 ( DEFAULT FROM FUNCTION )
    # SHUFFLE THE DATASET
    # THE RESULT IS A TENSORFLOW DATASET OBJECT THAT HOLDS THE IMAGE DATA (x) AND THE CORRESPONDING LABELS (y)
    data = tf.keras.utils.image_dataset_from_directory('data')

    # NORMALIZING THE IMAGE
    # WILL MAKE EACH IMAGE WHICH IS 256 X 256 AND MAKE INTO x-PIXEL/255 X y-PIXEL/255
    # WILL MAKE PROCESSING IMAGE FASTER BECAUSE THE VALUE OF EACH PIXEL IS RANGE BETWEEN 0 AND 1
    data = data.map(lambda x,y: (x/255, y))


    # DIVIDED TRAINING, VALIDATION AND TEST DATASET BATCH SIZE
    val_size = math.ceil(0.2 * len(data))
    test_size = math.ceil(0.1 * len(data))
    train_size = len(data) - val_size - test_size

    train = data.take(train_size)
    val = data.skip(train_size).take(val_size)
    test = data.skip(train_size + val_size).take(test_size)

    model = getModel()
    
    # TRAIN THE MODEL

    logdir='logs'
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)
    hist = model.fit(train, epochs=20, validation_data=val, callbacks=[tensorboard_callback])

    fig = plt.figure()
    plt.plot(hist.history['loss'], color='teal', label='loss')
    plt.plot(hist.history['val_loss'], color='orange', label='val_loss')
    fig.suptitle('Loss', fontsize=20)
    plt.legend(loc="upper left")
    plt.savefig(f"validation/loss/model-{GetLastModelCount() + 1}.png")

    fig = plt.figure()
    plt.plot(hist.history['accuracy'], color='teal', label='accuracy')
    plt.plot(hist.history['val_accuracy'], color='orange', label='val_accuracy')
    fig.suptitle('Accuracy', fontsize=20)
    plt.legend(loc="upper left")
    plt.savefig(f"validation/accuracy/model-{GetLastModelCount() + 1}.png")

    # SAVE GENERATED MODEL IN LOCAL FILE
    model.save(os.path.join('models', f"model-{GetLastModelCount() + 1}.h5"))