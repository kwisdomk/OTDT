"""

LSTM Failure Predictor.

Input: sliding window of 60 timesteps x 6 sensor features

Output: P(failure_imminent) for next timestep

"""

import numpy as np

import tensorflow as tf

from tensorflow.keras import layers, models


FEATURES     = ['bearing_temp_c','bearing_vibration_mms','steam_inlet_temp_c',

                'steam_inlet_pressure_bar','turbine_rpm','steam_flow_kgs']

FEATURE_MAX  = [105.0, 7.1, 280.0, 85.0, 3100.0, 55.0]

WINDOW       = 60    # seconds of history

BATCH_SIZE   = 256

EPOCHS       = 15


def build_model() -> tf.keras.Model:

    m = models.Sequential([

        layers.Input(shape=(WINDOW, len(FEATURES))),

        layers.LSTM(64, return_sequences=True),

        layers.Dropout(0.2),

        layers.LSTM(32),

        layers.Dropout(0.2),

        layers.Dense(16, activation='relu'),

        layers.Dense(1,  activation='sigmoid'),    # P(failure_imminent)

    ])

    m.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy','AUC'])

    return m


def make_windows(df, window=WINDOW):

    """Slice DataFrame into (X, y) sliding windows for LSTM training."""

    X_raw = df[FEATURES].values / FEATURE_MAX   # normalise 0-1

    y_raw = df['failure_imminent'].values

    X, y  = [], []

    for i in range(len(X_raw) - window):

        X.append(X_raw[i:i+window])

        y.append(y_raw[i+window])

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def train(df):

    X, y = make_windows(df)

    split = int(len(X) * 0.8)

    model = build_model()

    model.summary()

    history = model.fit(

        X[:split], y[:split],

        validation_data=(X[split:], y[split:]),

        epochs=EPOCHS, batch_size=BATCH_SIZE,

        callbacks=[tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)]

    )

    model.save('lstm_failure_predictor.h5')

    print('Model saved: lstm_failure_predictor.h5')

    return model, history


def predict(model, window_array: np.ndarray) -> float:

    """Single inference. window_array shape: (60, 6) normalised floats."""

    x = window_array.reshape(1, WINDOW, len(FEATURES))

    return float(model.predict(x, verbose=0)[0][0])


if __name__ == '__main__':

    import pandas as pd

    from data_generator import generate

    df = generate(days=365)

    train(df)
