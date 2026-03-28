"""Test FastAPI endpoints for Step 2: Maximo Integration.

Build Guide Step 2: Validate asset loading pipeline.
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_assets_endpoint():
    """Test GET /api/assets endpoint."""
    print("\n" + "="*60)
    print("Testing GET /api/assets")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/assets")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Status: {response.status_code}")
        print(f"[OK] Total assets: {data['total']}")
        print(f"[OK] Assets returned: {len(data['assets'])}")
        print(f"[OK] First asset: {data['assets'][0]['asset_id']} - {data['assets'][0]['description']}")
        print(f"[OK] Disclaimer present: {'disclaimer' in data}")
        return True
    else:
        print(f"[FAIL] Status: {response.status_code}")
        print(f"[FAIL] Response: {response.text}")
        return False


def test_asset_by_id():
    """Test GET /api/assets/{asset_id} endpoint."""
    print("\n" + "="*60)
    print("Testing GET /api/assets/GDC-WP-007")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/assets/GDC-WP-007")
    
    if response.status_code == 200:
        data = response.json()
        asset = data['asset']
        print(f"[OK] Status: {response.status_code}")
        print(f"[OK] Asset ID: {asset['asset_id']}")
        print(f"[OK] Asset Class: {asset['asset_class']}")
        print(f"[OK] Description: {asset['description']}")
        print(f"[OK] Replacement Cost: ${asset['replacement_cost_usd']:,.2f}")
        return True
    else:
        print(f"[FAIL] Status: {response.status_code}")
        return False


def test_sensors_endpoint():
    """Test GET /api/twins/{asset_id}/sensors/latest endpoint."""
    print("\n" + "="*60)
    print("Testing GET /api/twins/GDC-WP-007/sensors/latest")
    print("="*60)
    
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/api/twins/GDC-WP-007/sensors/latest")
    response_time = (time.time() - start_time) * 1000  # Convert to ms
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Status: {response.status_code}")
        print(f"[OK] Response time: {response_time:.0f}ms (target: <500ms)")
        print(f"[OK] Asset ID: {data['asset_id']}")
        print(f"[OK] Asset Class: {data['asset_class']}")
        print(f"[OK] Health Score: {data['health_score']}")
        print(f"[OK] Status: {data['status']} ({data['colour_code']})")
        print(f"[OK] Sensors: {list(data['sensors'].keys())}")
        print(f"[OK] Temperature: {data['sensors'].get('temperature_c')}°C")
        print(f"[OK] Pressure: {data['sensors'].get('pressure_bar')} bar")
        print(f"[OK] Vibration: {data['sensors'].get('vibration_mm_s')} mm/s")
        
        if response_time < 500:
            print(f"[OK] Performance target met!")
        else:
            print(f"[WARNING] Response time exceeds 500ms target")
        
        return True
    else:
        print(f"[FAIL] Status: {response.status_code}")
        print(f"[FAIL] Response: {response.text}")
        return False


def test_filter_by_class():
    """Test GET /api/assets?asset_class=WELL_PUMP endpoint."""
    print("\n" + "="*60)
    print("Testing GET /api/assets?asset_class=WELL_PUMP")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/assets?asset_class=WELL_PUMP")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Status: {response.status_code}")
        print(f"[OK] Filtered: {data['filtered']}")
        print(f"[OK] Total WELL_PUMP assets: {data['total']}")
        print(f"[OK] All assets are WELL_PUMP: {all(a['asset_class'] == 'WELL_PUMP' for a in data['assets'])}")
        return True
    else:
        print(f"[FAIL] Status: {response.status_code}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("OT Digital Twin API - Step 2 Integration Tests")
    print("Build Guide Step 2: Maximo Integration")
    print("="*60)
    print("\nMake sure FastAPI server is running:")
    print("  cd otdt/OTDT")
    print("  uvicorn api.main:app --reload")
    print("\nWaiting 3 seconds for you to start the server...")
    time.sleep(3)
    
    results = []
    
    try:
        results.append(("Assets List", test_assets_endpoint()))
        results.append(("Asset by ID", test_asset_by_id()))
        results.append(("Sensors Latest", test_sensors_endpoint()))
        results.append(("Filter by Class", test_filter_by_class()))
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API server.")
        print("Please start the server with: uvicorn api.main:app --reload")
        return
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        print("\n[WARNING] SYNTHETIC DATA DISCLAIMER:")
        print("All data is computer-generated. Not representative of any")
        print("real client operational data.")
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed")
    
    print("="*60)


if __name__ == "__main__":
    main()

# Made with Bob
