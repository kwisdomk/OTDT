"""Generates 1 year of synthetic geothermal turbine telemetry with labelled failure events."""

import numpy as np

import pandas as pd

from datetime import datetime, timedelta


def generate(days: int = 365, hz: int = 1, n_failures: int = 12) -> pd.DataFrame:

    n       = days * 86400 * hz

    t       = [datetime(2025,1,1) + timedelta(seconds=i) for i in range(n)]

    drift   = np.linspace(0, 2.0, n)          # bearing wears over the year

    noise   = np.random.randn(n)


    # Scatter failure events and label 1 hour before each

    fail_times = np.sort(np.random.choice(n, n_failures, replace=False))

    label      = np.zeros(n, dtype=int)

    for ft in fail_times:

        label[max(0, ft-3600):ft] = 1


    df = pd.DataFrame({

        'timestamp':                t,

        'bearing_temp_c':           np.clip(83 + drift*2 + label*22 + noise*1.2, 60, 130),

        'bearing_vibration_mms':    np.clip(4.2 + drift   + label*5  + noise*0.15, 1, 15),

        'steam_inlet_temp_c':       np.clip(245 + noise*3, 200, 300),

        'steam_inlet_pressure_bar': np.clip(68  + noise*1.5, 50, 100),

        'turbine_rpm':              np.clip(3000 + noise*8, 2800, 3200),

        'steam_flow_kgs':           np.clip(42  + noise*1.2, 25, 65),

        'failure_imminent':         label,

    })

    return df


if __name__ == '__main__':

    df = generate()

    df.to_csv('training_data.csv', index=False)

    print(f'Generated {len(df):,} rows  |  failure-labelled: {df.failure_imminent.sum():,}')
