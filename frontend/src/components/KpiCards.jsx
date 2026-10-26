import React from 'react';

export default function KpiCards({ summary }) {
  if (!summary) return null;

  const {
    fairness_score = 0,
    spearman_rho = 0,
    total_students = 0,
    flagged_count = 0,
    flagged_rate = 0,
    compliance_rate = 0,
    hard_rule_violations = 0,
  } = summary;

  const scoreClass =
    fairness_score >= 85 ? 'kpi-good' : fairness_score >= 70 ? 'kpi-warn' : 'kpi-bad';

  return (
    <div className="kpi-grid">
      <div className={`kpi-card ${scoreClass}`}>
        <div className="kpi-label">Fairness Score (Spearman ρ)</div>
        <div className="kpi-value">{fairness_score} <span className="kpi-sub">/ 100</span></div>
        <div className="kpi-footnote">Correlation ρ = {spearman_rho}</div>
      </div>

      <div className="kpi-card">
        <div className="kpi-label">Violations Flagged</div>
        <div className="kpi-value kpi-bad-text">{flagged_count}</div>
        <div className="kpi-footnote">{flagged_rate}% of cohort ({hard_rule_violations} accessibility)</div>
      </div>

      <div className="kpi-card">
        <div className="kpi-label">Allocations Audited</div>
        <div className="kpi-value">{summary.total_allocated || total_students}</div>
        <div className="kpi-footnote">out of {total_students} student applicants</div>
      </div>

      <div className="kpi-card">
        <div className="kpi-label">Policy Compliance Rate</div>
        <div className="kpi-value kpi-good-text">{compliance_rate}%</div>
        <div className="kpi-footnote">{summary.fair_count} allocations within tolerance</div>
      </div>
    </div>
  );
}
