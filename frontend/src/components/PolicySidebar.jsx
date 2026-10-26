import React from 'react';

export default function PolicySidebar({ weights, onChange, onReset, isAuditing }) {
  const handleSliderChange = (key, value) => {
    onChange({ ...weights, [key]: parseFloat(value) });
  };

  return (
    <aside className="policy-sidebar">
      <div className="sidebar-header">
        <h3>Policy What-If Weights</h3>
        <p className="sidebar-sub">Live recalculation on slider change</p>
      </div>

      <div className="slider-group">
        <div className="slider-label-row">
          <span>CGPA Merit Weight</span>
          <span className="slider-val">{Math.round((weights.w_cgpa || 0.35) * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.05"
          max="0.80"
          step="0.05"
          value={weights.w_cgpa ?? 0.35}
          onChange={(e) => handleSliderChange('w_cgpa', e.target.value)}
        />
      </div>

      <div className="slider-group">
        <div className="slider-label-row">
          <span>Home Distance Weight</span>
          <span className="slider-val">{Math.round((weights.w_distance || 0.20) * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.05"
          max="0.60"
          step="0.05"
          value={weights.w_distance ?? 0.20}
          onChange={(e) => handleSliderChange('w_distance', e.target.value)}
        />
      </div>

      <div className="slider-group">
        <div className="slider-label-row">
          <span>Seniority (Year) Weight</span>
          <span className="slider-val">{Math.round((weights.w_year || 0.20) * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.05"
          max="0.50"
          step="0.05"
          value={weights.w_year ?? 0.20}
          onChange={(e) => handleSliderChange('w_year', e.target.value)}
        />
      </div>

      <div className="slider-group">
        <div className="slider-label-row">
          <span>Reservation Bonus Weight</span>
          <span className="slider-val">{Math.round((weights.w_category || 0.10) * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.0"
          max="0.40"
          step="0.05"
          value={weights.w_category ?? 0.10}
          onChange={(e) => handleSliderChange('w_category', e.target.value)}
        />
      </div>

      <div className="slider-group">
        <div className="slider-label-row">
          <span>Special Needs (PwD) Weight</span>
          <span className="slider-val">{Math.round((weights.w_special_needs || 0.15) * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.05"
          max="0.50"
          step="0.05"
          value={weights.w_special_needs ?? 0.15}
          onChange={(e) => handleSliderChange('w_special_needs', e.target.value)}
        />
      </div>

      <div className="slider-group tolerance-group">
        <div className="slider-label-row">
          <span>Tolerance Threshold</span>
          <span className="slider-val">{Math.round(weights.tolerance_pct ?? 10)}% of rooms</span>
        </div>
        <input
          type="range"
          min="2"
          max="25"
          step="1"
          value={weights.tolerance_pct ?? 10}
          onChange={(e) => handleSliderChange('tolerance_pct', e.target.value)}
        />
      </div>

      <button className="reset-btn" onClick={onReset} disabled={isAuditing}>
        {isAuditing ? 'Auditing...' : 'Reset Policy Defaults'}
      </button>
    </aside>
  );
}
