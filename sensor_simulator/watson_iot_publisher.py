import json, time, sys

import paho.mqtt.client as mqtt

from config import ORG, ASSET_TYPE, ASSET_ID, AUTH_TOKEN, INTERVAL

from simulator import GeothermalSimulator


BROKER    = f'{ORG}.messaging.internetofthings.ibmcloud.com'

PORT      = 8883

CLIENT_ID = f'd:{ORG}:{ASSET_TYPE}:{ASSET_ID}'

TOPIC     = 'iot-2/evt/sensor/fmt/json'


sim = GeothermalSimulator()


def on_connect(client, userdata, flags, rc):

    codes = {0:'Connected',1:'Bad protocol',2:'Client ID rejected',3:'Server unavailable',

             4:'Bad credentials',5:'Not authorised'}

    print(f'[MQTT] {codes.get(rc, rc)}')


client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)

client.username_pw_set('use-token-auth', AUTH_TOKEN)   # Watson IoT auth

client.tls_set()                                        # TLS required

client.on_connect = on_connect

client.connect(BROKER, PORT)

client.loop_start()


print(f'[SIM] Publishing to {BROKER} every {INTERVAL}s  |  --demo for timed anomaly')


DEMO_MODE = '--demo' in sys.argv

demo_timer = 0


try:

    while True:

        if DEMO_MODE:

            demo_timer += INTERVAL

            if 60 <= demo_timer < 180 and not sim.anomaly_active:

                sim.inject_anomaly()

                print('[SIM] ANOMALY INJECTED at t=60s')

            elif demo_timer >= 180 and sim.anomaly_active:

                sim.clear_anomaly()

                print('[SIM] Anomaly cleared at t=180s')


        payload = json.dumps(sim.get_reading())

        result  = client.publish(TOPIC, payload, qos=1)

        print(f'[SIM] rc={result.rc}  {payload[:100]}')

        time.sleep(INTERVAL)


except KeyboardInterrupt:

    print('[SIM] Stopped')

    client.loop_stop()

# Test: does the reading match the contract?

python3 -c "

from simulator import GeothermalSimulator

import json

sim = GeothermalSimulator()

r = sim.get_reading()

required = ['asset_id','asset_type','timestamp','sensors','is_anomaly_injected']

sensors  = ['bearing_temp_c','bearing_vibration_mms','steam_inlet_temp_c',

            'steam_inlet_pressure_bar','turbine_rpm','steam_flow_kgs']

assert all(k in r for k in required)

assert all(k in r['sensors'] for k in sensors)

print('Contract OK')

print(json.dumps(r, indent=2))

"


# Test: anomaly injection spikes correctly?

python3 -c "

from simulator import GeothermalSimulator

sim = GeothermalSimulator()

sim.inject_anomaly()

r = sim.get_reading()

assert r['sensors']['bearing_vibration_mms'] > 7.1, 'Anomaly not in critical zone'

print('Anomaly OK  vib=', r['sensors']['bearing_vibration_mms'])

"
