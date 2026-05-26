import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useWebSocket } from './hooks/useWebSocket';
import WhatIfSlider from './components/WhatIfSlider';
import WatsonXQueryPanel from './components/WatsonXQueryPanel';
import './App.css';

// Human-readable sensor config. Baseline keys are primary; legacy stream keys
// remain accepted until the sensor-contract migration is resolved.
const SENSOR_META = {
  temperature_c:           { label: 'Temperature',     unit: '°C'   },
  pressure_bar:            { label: 'Pressure',        unit: 'bar'  },
  vibration_mm_s:          { label: 'Vibration',       unit: 'mm/s' },
  flow_rate_kg_s:          { label: 'Flow Rate',       unit: 'kg/s' },
  rotation_rpm:            { label: 'Rotation',        unit: 'rpm'  },
  bearing_temp_c:          { label: 'Bearing Temp',    unit: '°C'   },
  bearing_vibration_mms:   { label: 'Vibration',       unit: 'mm/s' },
  steam_inlet_temp_c:      { label: 'Steam Inlet Temp',unit: '°C'   },
  steam_inlet_pressure_bar:{ label: 'Steam Pressure',  unit: 'bar'  },
  turbine_rpm:             { label: 'Turbine RPM',     unit: 'rpm'  },
  steam_flow_kgs:          { label: 'Steam Flow',      unit: 'kg/s' },
  vibration_mms:           { label: 'Vibration',       unit: 'mm/s' },
  flow_rate_ls:            { label: 'Flow Rate',       unit: 'L/s'  },
};

const fmt = (val, dp = 2) =>
  val == null || isNaN(val) ? '—' : Number(val).toFixed(dp);

const probClass = (p) => {
  if (p == null) return 'standby';
  if (p >= 0.25) return 'high';
  if (p >= 0.10) return 'medium';
  return 'low';
};

export default function App() {
  const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/twin/stream';
  const { data, status } = useWebSocket(WS_URL);

  const [asset, setAsset]     = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!data?.assets?.length) return;
    const a = data.assets[0];
    setAsset(a);
    const vib = a?.sensors?.vibration_mm_s ?? a?.sensors?.bearing_vibration_mms ?? a?.sensors?.vibration_mms;
    if (vib != null) {
      setHistory(prev => [
        ...prev.slice(-19),
        { t: new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }), v: +vib.toFixed(3) }
      ]);
    }
  }, [data]);

  const currentStatus = asset?.status || 'NORMAL';
  const failureProb   = asset?.failure_probability ?? asset?.projected_failure_probability ?? null;
  const sensors       = asset?.sensors || {};

  return (
    <div>
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <h1>OT Digital Twin — GDC Kenya</h1>
          <p>Agentic AI Platform · i3 Technologies · IBM Research Lab Africa</p>
        </div>
        <div className="header-right">
          <div className="ws-indicator">
            <span className={`ws-dot ${status !== 'connected' ? 'disconnected' : ''}`} />
            {status.toUpperCase()}
          </div>
        </div>
      </header>

      {/* Disclaimer */}
      <div className="disclaimer">
        ⚠ SYNTHETIC DATA — All sensor readings and AI predictions are computer-generated simulation outputs. Not real plant data.
      </div>

      <div className="main">
        {asset ? (
          <>
            {/* Status Banner */}
            <div className={`status-banner ${currentStatus}`}>
              <div>
                <div className="status-asset">{asset.asset_label || asset.asset_id}</div>
                <div className="status-sub">Well Pump · Geothermal Pad 1 · GDC Kenya</div>
              </div>
              <div className="status-badge">{currentStatus}</div>
            </div>

            <div className="grid-two">
              {/* LEFT column */}
              <div>
                {/* Sensor Cards */}
                <div className="sensor-grid">
                  {Object.entries(sensors).map(([key, val]) => {
                    const meta = SENSOR_META[key] || { label: key, unit: '' };
                    return (
                      <div key={key} className={`sensor-card status-${currentStatus}`}>
                        <div className="sensor-label">{meta.label}</div>
                        <div className="sensor-value">
                          {fmt(val, key.includes('rpm') ? 0 : 2)}
                          <span className="sensor-unit">{meta.unit}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Vibration Trend */}
                <div className="card">
                  <div className="card-title">Vibration Trend — Last 20 readings (mm/s)</div>
                  <div className="trend-container">
                    {history.length > 1 ? (
                      <ResponsiveContainer width="100%" height={180}>
                        <LineChart data={history} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                          <XAxis dataKey="t" hide />
                          <YAxis domain={[0, 12]} tick={{ fontSize: 10, fontFamily: 'IBM Plex Mono' }} />
                          <Tooltip
                            contentStyle={{ fontSize: 12, fontFamily: 'IBM Plex Mono', border: '1px solid #d1d9e6' }}
                            formatter={(v) => [`${v} mm/s`, 'Vibration']}
                          />
                          <Line
                            type="monotone"
                            dataKey="v"
                            stroke={currentStatus === 'CRITICAL' ? '#b91c1c' : currentStatus === 'WARNING' ? '#b45309' : '#2E6FA3'}
                            strokeWidth={2}
                            dot={false}
                            isAnimationActive={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div style={{ height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <span className="loading-text">Collecting data...</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* RIGHT column */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                {/* Failure Probability */}
                <div className="card prob-card">
                  <div className="prob-label">Monte Carlo Failure Probability</div>
                  <div className={`prob-value ${probClass(failureProb)}`}>
                    {failureProb != null ? `${(failureProb * 100).toFixed(1)}%` : 'Standby'}
                  </div>
                  {typeof asset.days_to_failure_p50 === 'number' && asset.days_to_failure_p50 > 0 && (
                    <div className="prob-days">~{asset.days_to_failure_p50} days to failure (P50)</div>
                  )}
                  {asset.recommended_action && (
                    <span className={`prob-action action-${asset.recommended_action}`}>
                      {asset.recommended_action.replace('_', ' ')}
                    </span>
                  )}
                </div>

                {/* Work Order */}
                {asset.active_work_order_id && (
                  <div className="wo-card">
                    <div>
                      <div className="wo-label">Maximo Work Order Created</div>
                      <div className="wo-id">{asset.active_work_order_id}</div>
                    </div>
                    <span style={{ fontSize: 28 }}>✓</span>
                  </div>
                )}

                {/* What-If */}
                <div className="card">
                  <div className="card-title">What-If Analyst</div>
                  <WhatIfSlider
                    assetId={asset.asset_id}
                    currentProb={failureProb ?? 0.08}
                  />
                </div>
              </div>
            </div>

            {/* IBM watsonx.ai NLP Query Panel */}
            <WatsonXQueryPanel />
          </>
        ) : (
          <div className="loading-screen">
            <div className="spinner" />
            <div className="loading-text">AWAITING SENSOR STREAM · {status.toUpperCase()}</div>
          </div>
        )}
      </div>

      <footer className="footer">
        SYNTHETIC DATA · i3 Technologies Ltd · IBM Silver Partner · East Africa Agentic AI Workshop 2026
      </footer>
    </div>
  );
}
