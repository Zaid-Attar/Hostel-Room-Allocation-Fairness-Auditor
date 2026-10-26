import React, { useState } from 'react';

export default function ViolationsTable({ pairs = [], onSelectStudent }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('priority_gap');
  const [sortAsc, setSortAsc] = useState(false);

  const filtered = pairs.filter((p) => {
    const q = searchTerm.toLowerCase();
    return (
      p.room_id.toLowerCase().includes(q) ||
      p.should_have.toLowerCase().includes(q) ||
      p.should_have_name.toLowerCase().includes(q) ||
      p.got_it.toLowerCase().includes(q) ||
      p.got_it_name.toLowerCase().includes(q)
    );
  });

  const sorted = [...filtered].sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }
    if (aVal < bVal) return sortAsc ? -1 : 1;
    if (aVal > bVal) return sortAsc ? 1 : -1;
    return 0;
  });

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="table-card">
      <div className="table-header-row">
        <div>
          <h4>Accountability Table: "Who Got It vs. Who Should Have"</h4>
          <p className="chart-desc">
            Direct side-by-side evidence of displaced deserving students and lower-priority beneficiaries.
          </p>
        </div>
        <div className="table-actions">
          <input
            type="text"
            className="search-input"
            placeholder="Search room or student..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="table-responsive">
        <table className="audit-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('room_id')} className="sortable-th">
                Room ID {sortField === 'room_id' ? (sortAsc ? '▲' : '▼') : ''}
              </th>
              <th>Entitled Deserving Student</th>
              <th onClick={() => handleSort('should_have_priority')} className="sortable-th">
                Entitled Priority {sortField === 'should_have_priority' ? (sortAsc ? '▲' : '▼') : ''}
              </th>
              <th>Actual Beneficiary</th>
              <th onClick={() => handleSort('got_it_priority')} className="sortable-th">
                Beneficiary Priority {sortField === 'got_it_priority' ? (sortAsc ? '▲' : '▼') : ''}
              </th>
              <th onClick={() => handleSort('priority_gap')} className="sortable-th">
                Priority Inversion Gap {sortField === 'priority_gap' ? (sortAsc ? '▲' : '▼') : ''}
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center py-4 text-muted">
                  No line-jumping displacement pairs found matching current criteria.
                </td>
              </tr>
            ) : (
              sorted.map((p, idx) => (
                <tr key={`${p.room_id}-${idx}`}>
                  <td>
                    <span className="room-badge">{p.room_id}</span>
                  </td>
                  <td>
                    <button
                      className="link-btn"
                      onClick={() => onSelectStudent && onSelectStudent(p.should_have)}
                      title="Inspect student explainability"
                    >
                      {p.should_have_name} <span className="id-sub">({p.should_have})</span>
                    </button>
                  </td>
                  <td className="text-right">
                    <span className="score-badge good">{p.should_have_priority}</span>
                  </td>
                  <td>
                    <button
                      className="link-btn warn"
                      onClick={() => onSelectStudent && onSelectStudent(p.got_it)}
                      title="Inspect student explainability"
                    >
                      {p.got_it_name} <span className="id-sub">({p.got_it})</span>
                    </button>
                  </td>
                  <td className="text-right">
                    <span className="score-badge bad">{p.got_it_priority}</span>
                  </td>
                  <td className="text-right">
                    <span className="gap-tag">+{p.priority_gap} pts</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
