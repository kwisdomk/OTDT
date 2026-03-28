import os
from dotenv import load_dotenv
load_dotenv()

ASSET_ID    = os.getenv('WATSON_IOT_DEVICE_ID',   'GDC-TURBINE-01')
ASSET_TYPE  = os.getenv('WATSON_IOT_DEVICE_TYPE', 'geothermal_turbine')
ORG         = os.getenv('WATSON_IOT_ORG_ID')
AUTH_TOKEN  = os.getenv('WATSON_IOT_AUTH_TOKEN')
INTERVAL    = float(os.getenv('PUBLISH_INTERVAL_SECONDS', 1))

SENSOR_THRESHOLDS = {
    'bearing_temp_c':             {'warn': 90,   'crit': 105},
    'bearing_vibration_mms':      {'warn': 5.0,  'crit': 7.1},
    'steam_inlet_temp_c':         {'warn': 260,  'crit': 280},
    'steam_inlet_pressure_bar':   {'warn': 75,   'crit': 85},
    'turbine_rpm':                {'warn': 3060, 'crit': 3100},
    'steam_flow_kgs':             {'warn': 48,   'crit': 55},
}
