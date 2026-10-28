import React from 'react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine
} from 'recharts';

function CustomTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <div className="tooltip-title">{data.name} ({data.student_id})</div>
        <div className="tooltip-line">Priority Percentile: <strong>{data.priority_percentile}</strong></div>
        <div className="tooltip-line">Room Quality Percentile: <strong>{data.room_quality_percentile}</strong></div>
        <div className="tooltip-line">Room Assigned: <strong>{data.actual_room_id || 'None'}</strong></div>
        <div className={`tooltip-status status-${data.status.toLowerCase()}`}>
          Status: {data.status} {data.hard_rule_violation ? '(Accessibility Breach)' : ''}
        </div>
        <div className="tooltip-hint">Click point to view full explanation</div>
      </div>
    );
  }
  return null;
}

export default function PriorityScatter({ students = [], onSelectStudent }) {
  const allocated = students.filter((s) => s.actual_room_id !== null);

  const fairPoints = allocated.filter((s) => s.status === 'FAIR' && !s.hard_rule_violation);
  const overFavoredPoints = allocated.filter((s) => s.status === 'OVER_FAVORED');
  const underServedPoints = allocated.filter((s) => s.status === 'UNDER_SERVED' || s.hard_rule_violation);

  const handlePointClick = (entry) => {
    if (entry && entry.student_id && onSelectStudent) {
      onSelectStudent(entry.student_id);
    }
  };

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div className="chart-title-area">
          <h4>Hero Scatter: Priority Score vs. Room Quality Percentile</h4>
          <p className="chart-desc">
            The dashed diagonal is the ideal allocation (y = x). Points above are over-favored; points below are deprived.
          </p>
        </div>

        {/* Legend in top-right corner with inspection badge placed above it */}
        <div className="chart-corner-box">
          <span className="chart-badge">💡 Click any point to inspect</span>
          <div className="corner-legend">
            <div className="legend-row">
              <span className="legend-sym sym-fair">●</span>
              <span className="legend-lbl">Fair</span>
              <span className="legend-num">{fairPoints.length}</span>
            </div>
            <div className="legend-row">
              <span className="legend-sym sym-over">▲</span>
              <span className="legend-lbl">Over-Favored</span>
              <span className="legend-num">{overFavoredPoints.length}</span>
            </div>
            <div className="legend-row">
              <span className="legend-sym sym-under">■</span>
              <span className="legend-lbl">Under-Served</span>
              <span className="legend-num">{underServedPoints.length}</span>
            </div>
            <div className="legend-row">
              <span className="legend-sym sym-line">╌╌</span>
              <span className="legend-lbl">Ideal Line (y = x)</span>
            </div>
          </div>
        </div>
      </div>

      <div style={{ width: '100%', height: 460 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 35, bottom: 45, left: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#26334d" />
            <XAxis
              type="number"
              dataKey="priority_percentile"
              name="Priority Percentile"
              domain={[0, 102]}
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              tickLine={{ stroke: '#334155' }}
              axisLine={{ stroke: '#334155' }}
              label={{
                value: 'Priority Percentile (100 = Highest Merit)',
                position: 'insideBottom',
                offset: -20,
                fill: '#cbd5e1',
                fontSize: 12,
                style: { textAnchor: 'middle' }
              }}
            />
            <YAxis
              type="number"
              dataKey="room_quality_percentile"
              name="Room Quality Percentile"
              domain={[0, 102]}
              width={80}
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              tickLine={{ stroke: '#334155' }}
              axisLine={{ stroke: '#334155' }}
              label={{
                value: 'Room Quality Percentile (100 = Best Bed)',
                angle: -90,
                position: 'insideLeft',
                offset: 15,
                fill: '#cbd5e1',
                fontSize: 12,
                style: { textAnchor: 'middle' }
              }}
            />
            <ZAxis range={[55, 55]} />
            <Tooltip content={<CustomTooltip />} />

            {/* Ideal diagonal line y = x without colliding on-canvas text */}
            <ReferenceLine
              segment={[{ x: 0, y: 0 }, { x: 100, y: 100 }]}
              stroke="#64748b"
              strokeDasharray="5 5"
              strokeWidth={2}
            />

            <Scatter
              name="Fair Allocation"
              data={fairPoints}
              fill="#38bdf8"
              shape="circle"
              onClick={handlePointClick}
              cursor="pointer"
            />
            <Scatter
              name="Over-Favored"
              data={overFavoredPoints}
              fill="#ef4444"
              shape="triangle"
              onClick={handlePointClick}
              cursor="pointer"
            />
            <Scatter
              name="Under-Served"
              data={underServedPoints}
              fill="#f59e0b"
              shape="square"
              onClick={handlePointClick}
              cursor="pointer"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
