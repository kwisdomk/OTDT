"""
Maximo MAS 9.1 API client for work orders and alerts.
Mock implementation for demo — replace with real API when credentials available.
"""

import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('MAXIMO_BASE_URL', '')
USERNAME = os.getenv('MAXIMO_USERNAME', '')
PASSWORD = os.getenv('MAXIMO_PASSWORD', '')
SITE_ID = os.getenv('MAXIMO_SITE_ID', 'GDCKENYA')

_token = None

def _get_token() -> str:
    """Authenticate with Maximo and return session token."""
    global _token
    if _token:
        return _token
    
    if not BASE_URL or not USERNAME or not PASSWORD:
        print('[Maximo] Credentials not configured — using mock mode')
        return 'mock-token'
    
    try:
        creds = base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()
        headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}
        r = requests.post(f'{BASE_URL}/oslc/j_security_check', headers=headers, timeout=10)
        _token = r.cookies.get('LtpaToken2') or r.headers.get('X-Auth-Token', '')
        return _token
    except Exception as e:
        print(f'[Maximo] Auth failed: {e}')
        return ''

def create_work_order(asset_id: str, prob: float, scheduled_date: str) -> dict:
    """Create a work order in Maximo when failure probability > 0.25."""
    token = _get_token()
    
    # Mock response for demo when no real Maximo
    if not token or token == 'mock-token':
        print(f'[Maximo Mock] WO for {asset_id} at {prob*100:.0f}% risk')
        return {'work_order_id': f'MOCK-WO-{asset_id}', 'mock': True}
    
    headers = {
        'Cookie': f'LtpaToken2={token}',
        'Content-Type': 'application/json',
        'x-method-override': 'PATCH',
        'patchtype': 'MERGE',
        'Properties': 'wonum'
    }
    
    payload = {
        'siteid': SITE_ID,
        'assetnum': asset_id,
        'description': f'AI-GENERATED: Failure probability {prob*100:.0f}%',
        'wopriority': 1 if prob > 0.50 else 2,
        'wotype': 'PM',
        'schedstart': f'{scheduled_date}T08:00:00+03:00',
    }
    
    try:
        r = requests.post(f'{BASE_URL}/oslc/os/mxwo', json=payload, headers=headers, timeout=15)
        if r.status_code in (200, 201):
            wo_num = r.json().get('wonum', 'unknown')
            return {'work_order_id': f'WO-{wo_num}'}
        return {'error': r.status_code, 'detail': r.text[:200]}
    except Exception as e:
        return {'error': str(e)}

def get_active_alerts() -> list:
    """Get active Maximo Monitor alerts."""
    token = _get_token()
    
    if not token or token == 'mock-token':
        return [{'asset': 'WP-07', 'status': 'ACTIVE', 'desc': 'Mock alert'}]
    
    headers = {'Cookie': f'LtpaToken2={token}'}
    try:
        r = requests.get(
            f'{BASE_URL}/oslc/os/mxalert?oslc.where=status="ACTIVE"',
            headers=headers, timeout=10
        )
        return r.json().get('rdfs:member', []) if r.status_code == 200 else []
    except Exception:
        return []