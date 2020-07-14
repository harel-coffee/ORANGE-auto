import numpy as np
seed = 123
np.random.seed(seed)
from tensorflow.compat.v1 import set_random_seed
set_random_seed(seed)
import pickle as pk
import numpy as np
from keras.layers import GlobalMaxPooling2D
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
import pandas as pd
from keras.layers import Conv2D, Activation
from keras.models import Sequential
from keras.layers.core import Dense
from keras.layers.convolutional import MaxPooling2D
from keras.callbacks import EarlyStopping
from keras.layers.normalization import BatchNormalization
from keras import regularizers
import os
from sys import argv
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

dataset_name = argv[1]

pickle_train = open("dataset/"+dataset_name+"/"+dataset_name+"_train.pickle","rb")
X_train = pk.load(pickle_train)
X_train = np.asarray(X_train)

pickle_test = open("dataset/"+dataset_name+"/"+dataset_name+"_test.pickle","rb")
X_test = pk.load(pickle_test)
X_test = np.asarray(X_test)

image_size = X_train.shape[1]
X_train = np.reshape(X_train, [-1, image_size, image_size, 1])
X_test = np.reshape(X_test, [-1, image_size, image_size, 1])

y_train = pd.read_csv("dataset/"+dataset_name+"/"+dataset_name+"_train_norm.csv")
y_train = y_train[y_train.columns[-1]]

y_test = pd.read_csv("dataset/"+dataset_name+"/"+dataset_name+"_test_norm.csv")
y_test = y_test[y_test.columns[-1]]

model = Sequential()
reg = 0.0001
input_shape = (X_train.shape[1], X_train.shape[1], 1)
model.add(Conv2D(32, (2, 2), input_shape=input_shape, padding='same', kernel_initializer='glorot_uniform', kernel_regularizer=regularizers.l2(reg)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(64, (4, 4), padding='same', kernel_initializer='glorot_uniform', kernel_regularizer=regularizers.l2(reg)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(GlobalMaxPooling2D())
model.add(Dense(1, activation='sigmoid', name='act_output'))
model.summary()

from sklearn.model_selection import train_test_split
X_train, X_val, Y_train, Y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42, stratify=y_train, shuffle=True)

opt = Adam(lr = argv[2])
model.compile(optimizer=opt, loss= 'binary_crossentropy', metrics=['accuracy'])
early_stopping = EarlyStopping(monitor='val_loss', patience=20)
model_checkpoint = ModelCheckpoint("dataset/"+dataset_name+"/"+'model_{epoch:02d}-{val_loss:.2f}.h5', monitor='val_loss', verbose=0,
                                       save_best_only=True, save_weights_only=False, mode='auto')
lr_reducer = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, verbose=0, mode='auto',
                                   min_delta=0.0001, cooldown=0, min_lr=0)

model.fit(X_train, Y_train, epochs=200, batch_size=argv[3], verbose=1, callbacks=[early_stopping, lr_reducer], validation_data=[X_val, Y_val])
print("Train complete")