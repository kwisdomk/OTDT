from engine import run_simulation, DRIFT_RATE, THRESHOLDS

from datetime import datetime, timedelta


def optimal_schedule(sensor_state: dict) -> dict:

    """

    Binary search for the earliest date where failure_probability < 0.10.

    Returns schedule dict consumed by Maximo work order creation.

    """

    base  = run_simulation(sensor_state)

    if base['failure_probability'] < 0.10:

        return {**base, 'schedule_urgency': 'ROUTINE', 'schedule_window_days': 30}


    # Walk forward day by day until risk < 10%

    curr_vib = sensor_state['bearing_vibration_mms']

    for days_ahead in range(1, 31):

        projected_vib = curr_vib + (DRIFT_RATE * days_ahead)

        projected_state = {**sensor_state, 'bearing_vibration_mms': projected_vib}

        result = run_simulation(projected_state, n=1000)  # faster scan

        if result['failure_probability'] >= 0.50:

            return {

                **base,

                'schedule_urgency':    'URGENT',

                'schedule_window_days': days_ahead,

                'deadline_date':        (datetime.utcnow() + timedelta(days=days_ahead)).strftime('%Y-%m-%d'),

            }

    return {**base, 'schedule_urgency': 'MODERATE', 'schedule_window_days': 14}

