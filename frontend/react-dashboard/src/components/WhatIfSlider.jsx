import { useState } from 'react';

export default function WhatIfSlider({ assetId, currentProb }) {
  const [date, setDate] = useState('');
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
    <div style={{ padding: 16, border: '1px solid #ccc', borderRadius: 4 }}>
      <h4>What-If Analyst</h4>
      <p>Current failure probability: <strong style={{ color: '#C00000' }}>{pct(currentProb)}</strong></p>
      <label>
        If maintenance is performed on:
        <input
          type="date"
          value={date}
          onChange={(e) => simulate(e.target.value)}
          style={{ marginLeft: 8 }}
        />
      </label>
      {loading && <p>Simulating...</p>}
      {result && !loading && (
        <div>
          <p>
            Projected probability:{' '}
            <strong
              style={{
                color: result.failure_probability > 0.25 ? '#C00000' : '#1E6B3C',
              }}
            >
              {pct(result.failure_probability)}
            </strong>
          </p>
          <p>
            Recommended action: <strong>{result.recommended_action}</strong>
          </p>
        </div>
      )}
    </div>
  );
}
