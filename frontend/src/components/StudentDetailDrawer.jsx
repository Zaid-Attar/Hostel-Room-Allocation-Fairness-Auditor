import React, { useEffect, useState } from 'react';
import { getStudentExplanation } from '../api';

export default function StudentDetailDrawer({ studentId, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!studentId) return;
    setLoading(true);
    setError(null);
    getStudentExplanation(studentId)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [studentId]);

  if (!studentId) return null;

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <h3>Audit Explainability Inspector</h3>
            <p className="drawer-sub">Mathematical audit reasoning and factor decomposition</p>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        {loading ? (
          <div className="drawer-loading">Loading student audit breakdown...</div>
        ) : error ? (
          <div className="drawer-error">Error: {error}</div>
        ) : data ? (
          <div className="drawer-content">
            {/* Student Profile Card */}
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

            {/* Plain English Reason Box */}
            <div className="reason-box">
              <div className="reason-label">Plain-English Audit Finding:</div>
              <div className="reason-text">{data.reason}</div>
            </div>

            {/* Room Allocation Comparison */}
            <div className="comparison-grid">
              <div className="comparison-col">
                <span className="comp-label">Statutory Entitled Room</span>
                <span className="comp-value">{data.expected_room_id || 'None'}</span>
                <span className="comp-sub">Room Quality Rank #{data.expected_room_rank || 'N/A'}</span>
              </div>

              <div className="comparison-col">
                <span className="comp-label">Actual Received Room</span>
                <span className="comp-value">{data.actual_room_id || 'Unallocated'}</span>
                <span className="comp-sub">Room Quality Rank #{data.actual_room_rank || 'N/A'}</span>
              </div>

              <div className="comparison-col">
                <span className="comp-label">Disparity Deviation Gap</span>
                <span className={`comp-value ${data.deviation > 0 ? 'text-bad' : data.deviation < 0 ? 'text-warn' : 'text-good'}`}>
                  {data.deviation !== null ? `${data.deviation > 0 ? '+' : ''}${data.deviation} ranks` : 'N/A'}
                </span>
                <span className="comp-sub">
                  {data.deviation > 0 ? 'Demoted to lower room' : data.deviation < 0 ? 'Favoritism jump' : 'Within fair tolerance'}
                </span>
              </div>
            </div>

            {/* Factor Decomposition */}
            <div className="factors-section">
              <h4>Composite Priority Score: {data.priority_score} pts</h4>
              <p className="factors-desc">Contribution of each statutory policy component to final priority:</p>

              <div className="factors-table-wrap">
                <table className="factors-table">
                  <thead>
                    <tr>
                      <th>Factor</th>
                      <th>Applicant Value</th>
                      <th>Policy Weight</th>
                      <th>Normalized</th>
                      <th>Points Contributed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.factors &&
                      Object.entries(data.factors).map(([factorName, f]) => (
                        <tr key={factorName}>
                          <td className="factor-name-cell">
                            {factorName.replace('_', ' ').toUpperCase()}
                          </td>
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
        ) : null}
      </div>
    </div>
  );
}
