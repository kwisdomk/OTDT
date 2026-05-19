import React, { useState } from 'react';
import './WatsonXQueryPanel.css';

const WatsonXQueryPanel = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const exampleQueries = [
    "What if I defer WP-07 maintenance by 45 days?",
    "What happens if we delay GDC-HX-003 inspection for 60 days?",
    "Defer turbine TU-005 by 30 days",
    "What if we wait 90 days for pump 12?"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/watsonx/whatif-nlp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query.trim() }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(`Failed to process query: ${err.message}`);
      console.error('watsonx.ai query error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
    setError(null);
  };

  const getRiskColor = (probability) => {
    if (probability < 0.10) return '#28a745'; // Green
    if (probability < 0.25) return '#ffc107'; // Yellow
    if (probability < 0.50) return '#fd7e14'; // Orange
    return '#dc3545'; // Red
  };

  const getRiskLevel = (probability) => {
    if (probability < 0.10) return 'LOW';
    if (probability < 0.25) return 'MODERATE';
    if (probability < 0.50) return 'HIGH';
    return 'CRITICAL';
  };

  return (
    <div className="watsonx-query-panel">
      <div className="panel-header">
        <h2>Ask IBM watsonx.ai</h2>
        <div className="powered-by">
          <img 
            src="https://www.ibm.com/brand/experience-guides/developer/b1db1ae501d522a1a4b49613fe07c9f1/01_8-bar-positive.svg" 
            alt="IBM" 
            className="ibm-logo"
          />
          <span>Powered by IBM watsonx.ai</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask watsonx.ai: e.g. What if I defer WP-07 by 45 days?"
            className="query-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="submit-button"
            disabled={loading || !query.trim()}
          >
            {loading ? 'Processing...' : 'Ask'}
          </button>
        </div>

        <div className="example-queries">
          <span className="example-label">Try these examples:</span>
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              type="button"
              className="example-button"
              onClick={() => handleExampleClick(example)}
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </form>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="result-panel">
          <div className="result-header">
            <h3>Analysis Results</h3>
            <span className="model-badge">granite-13b-chat-v2</span>
          </div>

          <div className="extraction-info">
            <div className="info-item">
              <span className="label">Extracted Asset:</span>
              <span className="value asset-id">{result.extracted_asset_id}</span>
            </div>
            <div className="info-item">
              <span className="label">Deferral Period:</span>
              <span className="value">{result.extracted_deferral_days} days</span>
            </div>
            <div className="info-item">
              <span className="label">Maintenance Date:</span>
              <span className="value">{result.maintenance_date}</span>
            </div>
          </div>

          <div className="probability-section">
            <div className="probability-card">
              <div className="probability-header">
                <span>Failure Probability</span>
                <span 
                  className="risk-badge"
                  style={{ backgroundColor: getRiskColor(result.failure_probability) }}
                >
                  {getRiskLevel(result.failure_probability)}
                </span>
              </div>
              <div 
                className="probability-value"
                style={{ color: getRiskColor(result.failure_probability) }}
              >
                {result.failure_probability_percent}
              </div>
              <div className="probability-bar">
                <div 
                  className="probability-fill"
                  style={{ 
                    width: `${result.failure_probability * 100}%`,
                    backgroundColor: getRiskColor(result.failure_probability)
                  }}
                />
              </div>
            </div>

            <div className="cost-card">
              <div className="cost-label">Expected Cost</div>
              <div className="cost-value">
                ${result.expected_cost_usd.toLocaleString()}
              </div>
              <div className="cost-detail">
                Replacement Cost: ${result.replacement_cost_usd.toLocaleString()}
              </div>
            </div>
          </div>

          <div className="recommendation-section">
            <div className="recommendation-header">
              <strong>Recommendation:</strong>
            </div>
            <div className="recommendation-text">
              {result.recommendation}
            </div>
          </div>

          <div className="disclaimer">
            {result.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
};

export default WatsonXQueryPanel;

// Made with Bob
