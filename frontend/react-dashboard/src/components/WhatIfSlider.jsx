import { useState } from 'react';

export default function WhatIfSlider({ assetId, currentProb }) {
  const defaultDate = new Date();
  defaultDate.setDate(defaultDate.getDate() + 30);
  const defaultDateStr = defaultDate.toISOString().split('T')[0];

  const [date, setDate] = useState(defaultDateStr);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulate = async (d) => {
    setDate(d);
    setLoading(true);
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/whatif/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset_id: assetId, maintenance_date: d }),
      });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  };

  const pct = (v) => `${(v * 100).toFixed(1)}%`;

  return (
    <div style={{ padding: 16 }}>
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 14, color: '#666', marginBottom: 8 }}>Current Failure Probability</div>
        <div style={{ fontSize: 32, fontWeight: 'bold', color: currentProb > 0.25 ? '#C00000' : '#1E6B3C' }}>
          {pct(currentProb)}
        </div>
      </div>

      <div style={{ marginBottom: 20 }}>
        <label style={{ fontSize: 14, color: '#333', display: 'block', marginBottom: 8 }}>
          If maintenance is performed on:
        </label>
        <input
          type="date"
          value={date}
          onChange={(e) => simulate(e.target.value)}
          style={{
            padding: '10px 12px',
            fontSize: 14,
            border: '1px solid #ccc',
            borderRadius: 8,
            width: '100%',
            maxWidth: '200px'
          }}
        />
      </div>

      {loading && (
        <div style={{ color: '#666', fontSize: 13, marginTop: 12 }}>
          Running 10,000 simulations...
        </div>
      )}

      {result && !loading && (
        <div style={{
          marginTop: 16,
          padding: 16,
          background: '#f5f5f5',
          borderRadius: 8,
          borderLeft: `4px solid ${result.failure_probability > 0.25 ? '#C00000' : '#1E6B3C'}`
        }}>
          <div style={{ fontSize: 13, color: '#666', marginBottom: 8 }}>Projected Failure Probability</div>
          <div style={{ fontSize: 28, fontWeight: 'bold', color: result.failure_probability > 0.25 ? '#C00000' : '#1E6B3C' }}>
            {pct(result.failure_probability)}
          </div>
          {result.recommended_action && (
            <div style={{ marginTop: 12, fontSize: 13 }}>
              Recommended: <strong>{result.recommended_action}</strong>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
