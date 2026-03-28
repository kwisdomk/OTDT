#!/usr/bin/env python3
"""OTDT Pipeline Validation Tests"""
import sys, json
sys.path.insert(0, 'sensor_simulator')
from simulator import GeothermalSimulator
from config import SENSOR_THRESHOLDS

def test_simulator_contract():
    sim = GeothermalSimulator()
    r = sim.get_reading()
    required = ['asset_id','asset_type','timestamp','sensors','is_anomaly_injected']
    sensors  = ['bearing_temp_c','bearing_vibration_mms','steam_inlet_temp_c',
                'steam_inlet_pressure_bar','turbine_rpm','steam_flow_kgs']
    assert all(k in r for k in required), f'Missing keys: {[k for k in required if k not in r]}'
    assert all(k in r['sensors'] for k in sensors), f'Missing sensors: {[k for k in sensors if k not in r["sensors"]]}'
    print('✅ Simulator contract OK')
    print(json.dumps(r, indent=2))

def test_anomaly_injection():
    sim = GeothermalSimulator()
    sim.inject_anomaly()
    r = sim.get_reading()
    assert r['sensors']['bearing_vibration_mms'] > 7.1, f'Vib={r["sensors"]["bearing_vibration_mms"]} not critical'
    print('✅ Anomaly injection OK')
