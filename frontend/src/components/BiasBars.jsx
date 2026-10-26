import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell
} from 'recharts';

export default function BiasBars({ groupStats = {}, tolerance = 15 }) {
  const [selectedGroup, setSelectedGroup] = useState('category');
  const [metric, setMetric] = useState('average_deviation'); // 'average_deviation' or 'flagged_percent'

  const currentData = groupStats[selectedGroup] || [];

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div>
          <h4>Demographic Bias Breakdown</h4>
          <p className="chart-desc">
            Detects systematic institutional prejudice across social categories and demographics.
          </p>
        </div>

        <div className="bias-controls">
          <select
            className="filter-select"
            value={selectedGroup}
            onChange={(e) => setSelectedGroup(e.target.value)}
          >
            <option value="category">Statutory Category</option>
            <option value="year">Year of Study</option>
            <option value="distance_band">Distance Band</option>
            <option value="gender">Gender</option>
          </select>

          <div className="toggle-btn-group">
            <button
              className={`toggle-btn ${metric === 'average_deviation' ? 'active' : ''}`}
              onClick={() => setMetric('average_deviation')}
            >
              Avg Deviation
            </button>
            <button
              className={`toggle-btn ${metric === 'flagged_percent' ? 'active' : ''}`}
              onClick={() => setMetric('flagged_percent')}
            >
              % Flagged
            </button>
          </div>
        </div>
      </div>

      <div style={{ width: '100%', height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={currentData}
            margin={{ top: 10, right: 30, left: 20, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              type="number"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              label={{
                value: metric === 'average_deviation' ? 'Average Rank Deviation (Positive = Worse than fair)' : 'Flagged Violation Rate (%)',
                position: 'insideBottom',
                offset: -5,
                fill: '#cbd5e1'
              }}
            />
            <YAxis
              type="category"
              dataKey="group"
              tick={{ fill: '#cbd5e1', fontSize: 12 }}
              width={100}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="custom-tooltip">
                      <div className="tooltip-title">{d.group}</div>
                      <div className="tooltip-line">Total Cohort: <strong>{d.count}</strong></div>
                      <div className="tooltip-line">Average Deviation: <strong>{d.average_deviation}</strong></div>
                      <div className="tooltip-line">Flagged Rate: <strong>{d.flagged_percent}%</strong> ({d.flagged_count} students)</div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey={metric} radius={[0, 4, 4, 0]}>
              {currentData.map((entry, index) => {
                const isOverTolerance =
                  metric === 'average_deviation'
                    ? Math.abs(entry.average_deviation) >= (tolerance / 2)
                    : entry.flagged_percent >= 15;
                return (
                  <Cell
                    key={`cell-${index}`}
                    fill={isOverTolerance ? '#ef4444' : '#38bdf8'}
                  />
                );
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
