import { useState, useEffect, useCallback } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const pct = (v) => (v != null ? `${(v * 100).toFixed(1)}%` : '—');

const actionClass = (a) => {
  if (!a) return '';
  return `whatif-action-val action-${a}`;
};

const probColour = (p) => {
  if (p == null) return '#64748b';
  if (p >= 0.25) return '#b91c1c';
  if (p >= 0.10) return '#b45309';
  return '#1a7a3f';
};

export default function WhatIfSlider({ assetId, currentProb }) {
  const defaultDate = (() => {
    const d = new Date();
    d.setDate(d.getDate() + 30);
    return d.toISOString().split('T')[0];
  })();

  const today = new Date().toISOString().split('T')[0];

  const [date, setDate]     = useState(defaultDate);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);

  const simulate = useCallback(async (d) => {
    if (!d) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/whatif/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset_id: assetId, maintenance_date: d }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [assetId]);

  // Auto-fire when asset is available
  useEffect(() => {
    if (!assetId) return;
    simulate(defaultDate);
  }, [assetId, defaultDate, simulate]);

  return (
    <div>
      <div className="whatif-row">
        <span className="whatif-label">
          Current: <strong style={{ color: probColour(currentProb) }}>{pct(currentProb)}</strong>
        </span>
        <span className="whatif-label">→ If maintained on:</span>
        <input
          type="date"
          className="whatif-input"
          value={date}
          min={today}
          onChange={(e) => { setDate(e.target.value); simulate(e.target.value); }}
        />
      </div>

      {loading && (
        <div style={{ fontSize: 12, fontFamily: 'IBM Plex Mono', color: '#64748b', padding: '8px 0' }}>
          Running 10,000 simulations...
        </div>
      )}

      {error && (
        <div style={{ fontSize: 12, color: '#b91c1c', padding: '8px 0' }}>Error: {error}</div>
      )}

      {result && !loading && (() => {
        const projected =
          typeof result.failure_probability === 'number'
            ? result.failure_probability
            : typeof result.projected_failure_probability === 'number'
              ? result.projected_failure_probability
              : null;

        return (
        <div className="whatif-result">
          <div>
            <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b', marginBottom: 4 }}>
              Projected probability
            </div>
            <div className="whatif-prob-val" style={{ color: probColour(projected) }}>
              {pct(projected)}
            </div>
            <div style={{ fontSize: 11, color: '#64748b', fontFamily: 'IBM Plex Mono', marginTop: 4 }}>
              {result.days_deferred}d deferred · ~{result.days_to_failure_p50}d to failure
            </div>
          </div>
          <span className={actionClass(result.recommended_action)}>
            {result.recommended_action?.replace(/_/g, ' ')}
          </span>
        </div>
        );
      })()}
    </div>
  );
}
