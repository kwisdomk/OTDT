import { useWebSocket } from './hooks/useWebSocket';
import WhatIfSlider from './components/WhatIfSlider';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function App() {
  const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/twin/stream';
  const { data, status } = useWebSocket(WS_URL);

  const assets = data?.assets || [];
  const turbine = assets.find(a => a.asset_id === 'GDC-WP-007');

  const statusColour = { NORMAL: '#1E6B3C', WARNING: '#C55A11', CRITICAL: '#C00000' };

  return (
    <div style={{ fontFamily: 'Arial', padding: 24 }}>
      <h1>OT Digital Twin — GDC Kenya</h1>
      <p>WebSocket: <strong style={{ color: status === 'connected' ? 'green' : 'orange' }}>{status}</strong></p>

      {turbine && (
        <div>
          {/* Status banner */}
          <div style={{
            background: statusColour[turbine.status],
            color: '#fff',
            padding: '12px 20px',
            borderRadius: 4,
            marginBottom: 16
          }}>
            <strong>{turbine.asset_label}</strong> — {turbine.status}
          </div>

          {/* Sensor grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 16 }}>
            {Object.entries(turbine.sensors || {}).map(([k, v]) => (
              <div key={k} style={{ border: '1px solid #ccc', padding: 12, borderRadius: 4 }}>
                <div style={{ fontSize: 12, color: '#888' }}>{k}</div>
                <div style={{ fontSize: 24, fontWeight: 'bold' }}>{v?.toFixed(2) ?? 'N/A'}</div>
              </div>
            ))}
          </div>

          {/* Failure probability gauge */}
          <div style={{ marginBottom: 16 }}>
            <strong>Failure Probability: </strong>
            <span style={{
              fontSize: 32,
              fontWeight: 'bold',
              color: turbine.failure_probability > 0.25 ? '#C00000' : '#1E6B3C'
            }}>
              {(turbine.failure_probability * 100).toFixed(1)}%
            </span>
            {turbine.days_to_failure_p50 && (
              <span style={{ marginLeft: 16, color: '#888' }}>
                ~{turbine.days_to_failure_p50} days to failure (P50)
              </span>
            )}
          </div>

          {/* Work Order panel */}
          {turbine.active_work_order_id && (
            <div style={{ background: '#E2F0D9', padding: 12, borderRadius: 4, marginBottom: 16 }}>
              <strong>Maximo Work Order Created:</strong> {turbine.active_work_order_id}
            </div>
          )}

          {/* What-If Analyst */}
          <WhatIfSlider assetId={turbine.asset_id} currentProb={turbine.failure_probability} />
        </div>
      )}

      {!turbine && (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <p>Waiting for sensor data from GDC-WP-007...</p>
          <p>Make sure the API is running and Kafka is sending data.</p>
        </div>
      )}
    </div>
  );
}
