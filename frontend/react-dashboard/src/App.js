import React, { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import WhatIfSlider from './components/WhatIfSlider';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './App.css';

const fmt = (val, decimals = 1) =>
  val == null || isNaN(val) ? '—' : val.toFixed(decimals);

export default function App() {
  const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/twin/stream';
  const { data, status } = useWebSocket(WS_URL);

  const [assetState, setAssetState] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (data?.assets?.length > 0) {
      const turbine = data.assets[0];
      setAssetState(turbine);

      if (turbine?.sensors?.vibration_mms) {
        setHistory(prev => {
          const updated = [...prev, {
            time: new Date().toLocaleTimeString().slice(-8),
            vibration: turbine.sensors.vibration_mms
          }];
          return updated.slice(-20);
        });
      }
    }
  }, [data]);

  const statusColour = {
    NORMAL: '#1E6B3C',
    WARNING: '#C55A11',
    CRITICAL: '#C00000'
  };

  const currentStatus = assetState?.status || 'NORMAL';
  const themeColor = statusColour[currentStatus] || '#1E6B3C';

  const sensorLabels = {
    temperature_c: 'Temperature',
    pressure_bar: 'Pressure',
    vibration_mms: 'Vibration',
    flow_rate_ls: 'Flow Rate'
  };

  const sensorUnits = {
    temperature_c: '°C',
    pressure_bar: 'bar',
    vibration_mms: 'mm/s',
    flow_rate_ls: 'L/s'
  };

  const failureProb = assetState?.failure_probability ?? null;
  const anomalyScore = assetState?.anomaly_score ?? null;
  const sensors = assetState?.sensors || {};

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', background: '#F3F4F6', minHeight: '100vh' }}>

      {/* Header */}
      <div style={{ background: '#1F4E79', color: 'white', padding: '20px 32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: 0 }}>OT Digital Twin</h1>
            <p style={{ margin: '4px 0 0', opacity: 0.8 }}>Agentic AI Platform · East Africa</p>
          </div>
          <div style={{
            color: status === 'connected' ? '#A5D6A5' : '#FFB74D',
            fontWeight: 'bold',
            fontSize: 14
          }}>
            ● {status.toUpperCase()}
          </div>
        </div>
      </div>

      <div style={{ padding: '24px 32px' }}>
        {assetState ? (
          <>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
              gap: 24,
              marginBottom: 24
            }}>

              {/* LEFT: Physical Telemetry */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

                {/* Status Banner */}
                <div style={{
                  background: themeColor,
                  color: 'white',
                  padding: '16px 24px',
                  borderRadius: 12,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <div style={{ fontSize: 20, fontWeight: 'bold' }}>
                      {assetState.asset_label || assetState.asset_id}
                    </div>
                    <div style={{ fontSize: 14, opacity: 0.9 }}>Well Pump · Pad 1</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 28, fontWeight: 'bold' }}>{assetState.status}</div>
                    <div style={{ fontSize: 12, opacity: 0.9 }}>
                      Anomaly: {anomalyScore !== null ? `${(anomalyScore * 100).toFixed(1)}%` : '—'}
                    </div>
                  </div>
                </div>

                {/* Sensor Cards */}
                <div className="sensor-grid">
                  {Object.entries(sensors).map(([key, value]) => (
                    <div key={key} className="sensor-card" style={{
                      background: 'white',
                      borderRadius: 12,
                      padding: '16px 20px',
                      borderLeft: `4px solid ${themeColor}`,
                      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                    }}>
                      <div style={{ fontSize: 13, color: '#666', textTransform: 'uppercase' }}>
                        {sensorLabels[key] || key}
                      </div>
                      <div style={{ fontSize: 28, fontWeight: 'bold', color: '#333' }}>
                        {fmt(value, key === 'vibration_mms' ? 3 : 1)}
                        <span style={{ fontSize: 14, fontWeight: 'normal', color: '#888', marginLeft: 4 }}>
                          {sensorUnits[key] || ''}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Vibration Trend */}
                <div style={{
                  background: 'white',
                  borderRadius: 12,
                  padding: '20px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}>
                  <h4 style={{ margin: '0 0 12px 0', fontSize: 14, color: '#666' }}>
                    📈 VIBRATION TREND (Last 20 readings)
                  </h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={history}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="time" hide />
                      <YAxis domain={[0, 12]} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="vibration"
                        stroke={themeColor}
                        strokeWidth={3}
                        dot={false}
                        isAnimationActive={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                  {history.length === 0 && (
                    <p style={{ textAlign: 'center', color: '#888', fontSize: 12, marginTop: 8 }}>
                      Waiting for vibration data...
                    </p>
                  )}
                </div>
              </div>

              {/* RIGHT: AI Forensics */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

                {/* Failure Probability */}
                <div style={{
                  background: 'white',
                  borderRadius: 12,
                  padding: '24px',
                  textAlign: 'center',
                  borderLeft: `8px solid ${themeColor}`,
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}>
                  <div style={{ fontSize: 14, color: '#666', marginBottom: 8 }}>
                    MONTE CARLO PREDICTION
                  </div>
                  <div style={{
                    fontSize: 56,
                    fontWeight: 'bold',
                    color: failureProb !== null && failureProb > 0.25 ? '#C00000' : '#1E6B3C'
                  }}>
                    {failureProb !== null
                      ? `${(failureProb * 100).toFixed(1)}%`
                      : <span style={{ color: '#888', fontSize: 32 }}>Standby</span>}
                  </div>
                  {assetState.days_to_failure_p50 > 0 && (
                    <div style={{ fontSize: 14, color: '#888', marginTop: 8 }}>
                      ~{assetState.days_to_failure_p50} days to failure (P50)
                    </div>
                  )}
                  {assetState.recommended_action && (
                    <div style={{
                      marginTop: 12,
                      padding: '8px 12px',
                      background: '#f0f0f0',
                      borderRadius: 8,
                      fontSize: 13
                    }}>
                      Recommended: <strong>{assetState.recommended_action}</strong>
                    </div>
                  )}
                </div>

                {/* What-If Analyst */}
                <div style={{
                  background: 'white',
                  borderRadius: 12,
                  padding: '20px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}>
                  <h3 style={{ margin: '0 0 16px 0', fontSize: 18, color: '#333' }}>📊 What-If Analyst</h3>
                  <WhatIfSlider
                    assetId={assetState.asset_id}
                    currentProb={failureProb !== null ? failureProb : 0.08}
                  />
                </div>

                {/* Work Order — conditional */}
                {assetState.active_work_order_id && (
                  <div style={{
                    background: '#E8F0E8',
                    borderRadius: 12,
                    padding: '20px',
                    textAlign: 'center',
                    border: '1px solid #C0D4C0',
                    animation: 'slideIn 0.5s ease'
                  }}>
                    <div style={{ fontSize: 14, color: '#2E6B2E', marginBottom: 8 }}>✓ MAXIMO WORK ORDER</div>
                    <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1E6B3C' }}>
                      {assetState.active_work_order_id}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div style={{
              marginTop: 32,
              paddingTop: 16,
              borderTop: '1px solid #ddd',
              textAlign: 'center',
              fontSize: 12,
              color: '#888'
            }}>
              <p>SYNTHETIC DATA — All sensor readings and predictions are computer-generated. Not real plant data.</p>
              <p>i3 Technologies Ltd · IBM Silver Partner · East Africa Agentic AI Workshop 2026</p>
            </div>
          </>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            background: 'white',
            borderRadius: 12,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{ color: '#333' }}>Waiting for Sensor Data</h2>
            <p style={{ color: '#666' }}>Connecting to WebSocket stream...</p>
            <p style={{ fontSize: 12, color: '#aaa', marginTop: 16 }}>Status: {status}</p>
          </div>
        )}
      </div>
    </div>
  );
}