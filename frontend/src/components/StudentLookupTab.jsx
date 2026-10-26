import React, { useState } from 'react';
import { getStudentExplanation } from '../api';

export default function StudentLookupTab() {
  const [queryId, setQueryId] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!queryId.trim()) return;

    setLoading(true);
    setError(null);
    setData(null);

    try {
      const res = await getStudentExplanation(queryId.trim().toUpperCase());
      setData(res);
    } catch (err) {
      setError(err.message || 'Student not found in audit database');
    } finally {
      setLoading(false);
    }
  };

  const sampleStudents = ['S_M_005', 'S_M_010', 'S_F_003', 'S_F_012', 'S_M_149'];

  return (
    <div className="tab-container">
      <div className="tab-header-card">
        <div className="tab-title-group">
          <h3>Individual Student Fairness Lookup</h3>
          <p className="chart-desc">
            Quickly check whether any specific student received a fair room assignment, their entitlement, and grievance reason.
          </p>
        </div>
      </div>

      <div className="table-card">
        <form onSubmit={handleSearch} className="lookup-form">
          <input
            type="text"
            className="search-input large"
            placeholder="Enter Student ID (e.g. S_M_005 or S_F_003)..."
            value={queryId}
            onChange={(e) => setQueryId(e.target.value)}
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Searching...' : 'Lookup Fairness'}
          </button>
        </form>

        <div className="quick-suggestions">
          <span>Click to try sample IDs: </span>
          {sampleStudents.map((id) => (
            <button
              key={id}
              type="button"
              className="suggestion-tag"
              onClick={() => {
                setQueryId(id);
                setLoading(true);
                setError(null);
                setData(null);
                getStudentExplanation(id)
                  .then(setData)
                  .catch((err) => setError(err.message))
                  .finally(() => setLoading(false));
              }}
            >
              {id}
            </button>
          ))}
        </div>

        {error && (
          <div className="lookup-error-box">
            <strong>Not Found:</strong> {error}
          </div>
        )}

        {data && (
          <div className="lookup-result-card">
            <div className="profile-hero">
              <div className="hero-left">
                <h2>{data.name}</h2>
                <span className="hero-id">{data.student_id}</span>
              </div>
              <div className="hero-right">
                <span className={`status-pill pill-${data.status.toLowerCase()}`}>
                  {data.status}
                </span>
                {data.hard_rule_violation && (
                  <span className="status-pill pill-breach">
                    PwD Accessibility Breach
                  </span>
                )}
              </div>
            </div>

            <div className="reason-box">
              <div className="reason-label">Official Finding:</div>
              <div className="reason-text">{data.reason}</div>
            </div>

            <div className="comparison-grid">
              <div className="comparison-col">
                <span className="comp-label">Statutory Entitled Room</span>
                <span className="comp-value">{data.expected_room_id || 'None'}</span>
                <span className="comp-sub">Room Quality Rank #{data.expected_room_rank || 'N/A'}</span>
              </div>

              <div className="comparison-col">
                <span className="comp-label">Actual Allocated Room</span>
                <span className="comp-value">{data.actual_room_id || 'Unallocated'}</span>
                <span className="comp-sub">Room Quality Rank #{data.actual_room_rank || 'N/A'}</span>
              </div>

              <div className="comparison-col">
                <span className="comp-label">Allocation Gap (Deviation)</span>
                <span className={`comp-value ${data.deviation > 0 ? 'text-bad' : data.deviation < 0 ? 'text-warn' : 'text-good'}`}>
                  {data.deviation !== null ? `${data.deviation > 0 ? '+' : ''}${data.deviation} ranks` : 'N/A'}
                </span>
                <span className="comp-sub">
                  {data.deviation > 0 ? 'Demoted' : data.deviation < 0 ? 'Unfairly favored' : 'Fair allotment'}
                </span>
              </div>
            </div>

            <div className="factors-section">
              <h4>Composite Merit Score: {data.priority_score} pts</h4>
              <div className="factors-table-wrap">
                <table className="factors-table">
                  <thead>
                    <tr>
                      <th>Factor</th>
                      <th>Value</th>
                      <th>Policy Weight</th>
                      <th>Normalized</th>
                      <th>Contribution</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.factors &&
                      Object.entries(data.factors).map(([k, f]) => (
                        <tr key={k}>
                          <td className="factor-name-cell">{k.replace('_', ' ').toUpperCase()}</td>
                          <td>{f.raw_value}</td>
                          <td>{Math.round(f.weight * 100)}%</td>
                          <td>{f.normalized !== undefined ? f.normalized : f.bonus_value ?? f.value}</td>
                          <td className="contribution-cell">+{f.contribution} pts</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
