import React, { useState, useEffect } from 'react';
import { getStudents, createStudent, updateStudent, deleteStudent, updateAllocation } from '../api';

export default function StudentsTab({ onDataChanged }) {
  const [students, setStudents] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters & Pagination
  const [category, setCategory] = useState('');
  const [gender, setGender] = useState('');
  const [year, setYear] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Add Form State
  const [showAddForm, setShowAddForm] = useState(false);
  const [newStudent, setNewStudent] = useState({
    student_id: '',
    name: '',
    gender: 'M',
    year: 1,
    cgpa: 7.5,
    category: 'General',
    distance_km: 150,
    special_needs: 0,
  });

  // Inline Editing State
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    fetchStudentList();
  }, [category, gender, year, search, page]);

  const fetchStudentList = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getStudents({
        category,
        gender,
        year: year ? parseInt(year) : undefined,
        search,
        page,
        page_size: pageSize,
      });
      setStudents(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStudent = async (e) => {
    e.preventDefault();
    try {
      await createStudent({
        ...newStudent,
        year: parseInt(newStudent.year),
        cgpa: parseFloat(newStudent.cgpa),
        distance_km: parseInt(newStudent.distance_km),
        special_needs: parseInt(newStudent.special_needs),
      });
      setShowAddForm(false);
      setNewStudent({
        student_id: '',
        name: '',
        gender: 'M',
        year: 1,
        cgpa: 7.5,
        category: 'General',
        distance_km: 150,
        special_needs: 0,
      });
      fetchStudentList();
      if (onDataChanged) onDataChanged();
    } catch (err) {
      alert(`Error creating student: ${err.message}`);
    }
  };

  const startEdit = (s) => {
    setEditingId(s.student_id);
    setEditForm({
      name: s.name,
      cgpa: s.cgpa,
      year: s.year,
      category: s.category,
      distance_km: s.distance_km,
      special_needs: s.special_needs,
      allocated_room_id: s.allocated_room_id || '',
    });
  };

  const saveEdit = async (studentId) => {
    try {
      await updateStudent(studentId, {
        name: editForm.name,
        cgpa: parseFloat(editForm.cgpa),
        year: parseInt(editForm.year),
        category: editForm.category,
        distance_km: parseInt(editForm.distance_km),
        special_needs: parseInt(editForm.special_needs),
      });

      // Update allocation if changed
      await updateAllocation(studentId, editForm.allocated_room_id.trim() || null);

      setEditingId(null);
      fetchStudentList();
      if (onDataChanged) onDataChanged();
    } catch (err) {
      alert(`Error updating student: ${err.message}`);
    }
  };

  const handleDelete = async (studentId) => {
    if (!window.confirm(`Are you sure you want to delete student ${studentId}?`)) return;
    try {
      await deleteStudent(studentId);
      fetchStudentList();
      if (onDataChanged) onDataChanged();
    } catch (err) {
      alert(`Error deleting student: ${err.message}`);
    }
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="tab-container">
      {/* Filters & Actions Bar */}
      <div className="tab-header-card">
        <div className="tab-title-group">
          <h3>Student Cohort Records</h3>
          <p className="chart-desc">
            Direct database management: filter by OBC or category, add applicants, edit details, or re-assign beds.
          </p>
        </div>

        <button
          className="btn-primary"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Cancel' : '+ Add New Student'}
        </button>
      </div>

      {/* Add Student Modal / Form */}
      {showAddForm && (
        <form onSubmit={handleCreateStudent} className="add-record-card">
          <h4>Enroll New Student Profile</h4>
          <div className="form-grid">
            <div className="form-group">
              <label>Student ID (e.g., S_M_999)</label>
              <input
                type="text"
                required
                value={newStudent.student_id}
                onChange={(e) => setNewStudent({ ...newStudent, student_id: e.target.value })}
                placeholder="S_M_201"
              />
            </div>
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                required
                value={newStudent.name}
                onChange={(e) => setNewStudent({ ...newStudent, name: e.target.value })}
                placeholder="Rahul Deshmukh"
              />
            </div>
            <div className="form-group">
              <label>Gender</label>
              <select
                value={newStudent.gender}
                onChange={(e) => setNewStudent({ ...newStudent, gender: e.target.value })}
              >
                <option value="M">Male (M)</option>
                <option value="F">Female (F)</option>
              </select>
            </div>
            <div className="form-group">
              <label>Year of Study</label>
              <select
                value={newStudent.year}
                onChange={(e) => setNewStudent({ ...newStudent, year: e.target.value })}
              >
                <option value={1}>1st Year</option>
                <option value={2}>2nd Year</option>
                <option value={3}>3rd Year</option>
                <option value={4}>4th Year</option>
              </select>
            </div>
            <div className="form-group">
              <label>CGPA (0 - 10)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="10"
                required
                value={newStudent.cgpa}
                onChange={(e) => setNewStudent({ ...newStudent, cgpa: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Category</label>
              <select
                value={newStudent.category}
                onChange={(e) => setNewStudent({ ...newStudent, category: e.target.value })}
              >
                <option value="General">General</option>
                <option value="OBC">OBC</option>
                <option value="SC">SC</option>
                <option value="ST">ST</option>
                <option value="EWS">EWS</option>
              </select>
            </div>
            <div className="form-group">
              <label>Distance from Home (km)</label>
              <input
                type="number"
                min="0"
                required
                value={newStudent.distance_km}
                onChange={(e) => setNewStudent({ ...newStudent, distance_km: e.target.value })}
              />
            </div>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={newStudent.special_needs === 1}
                  onChange={(e) =>
                    setNewStudent({ ...newStudent, special_needs: e.target.checked ? 1 : 0 })
                  }
                />
                {' '}Special Needs (PwD)
              </label>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">Save Student</button>
            <button type="button" className="btn-secondary" onClick={() => setShowAddForm(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Filter Row */}
      <div className="table-controls-row">
        <div className="filter-group-inline">
          <label>Category:</label>
          <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}>
            <option value="">All Categories</option>
            <option value="General">General</option>
            <option value="OBC">OBC</option>
            <option value="SC">SC</option>
            <option value="ST">ST</option>
            <option value="EWS">EWS</option>
          </select>
        </div>

        <div className="filter-group-inline">
          <label>Gender:</label>
          <select value={gender} onChange={(e) => { setGender(e.target.value); setPage(1); }}>
            <option value="">All Genders</option>
            <option value="M">Male (Boys)</option>
            <option value="F">Female (Girls)</option>
          </select>
        </div>

        <div className="filter-group-inline">
          <label>Year:</label>
          <select value={year} onChange={(e) => { setYear(e.target.value); setPage(1); }}>
            <option value="">All Years</option>
            <option value="1">1st Year</option>
            <option value="2">2nd Year</option>
            <option value="3">3rd Year</option>
            <option value="4">4th Year</option>
          </select>
        </div>

        <input
          type="text"
          className="search-input"
          placeholder="Search student ID or name..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />

        <span className="count-tag">Showing {students.length} of {total} records</span>
      </div>

      {/* Table */}
      <div className="table-card">
        {loading ? (
          <div className="text-center py-4 text-muted">Loading students...</div>
        ) : error ? (
          <div className="text-center py-4 text-bad">{error}</div>
        ) : (
          <div className="table-responsive">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Gender</th>
                  <th>Year</th>
                  <th>CGPA</th>
                  <th>Category</th>
                  <th>Distance</th>
                  <th>PwD</th>
                  <th>Allocated Room</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => {
                  const isEditing = editingId === s.student_id;
                  return (
                    <tr key={s.student_id}>
                      <td><strong>{s.student_id}</strong></td>

                      {/* Name */}
                      <td>
                        {isEditing ? (
                          <input
                            type="text"
                            className="inline-input"
                            value={editForm.name}
                            onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                          />
                        ) : (
                          s.name
                        )}
                      </td>

                      {/* Gender */}
                      <td>{s.gender}</td>

                      {/* Year */}
                      <td>
                        {isEditing ? (
                          <select
                            className="inline-select"
                            value={editForm.year}
                            onChange={(e) => setEditForm({ ...editForm, year: e.target.value })}
                          >
                            <option value={1}>1</option>
                            <option value={2}>2</option>
                            <option value={3}>3</option>
                            <option value={4}>4</option>
                          </select>
                        ) : (
                          `Yr ${s.year}`
                        )}
                      </td>

                      {/* CGPA */}
                      <td>
                        {isEditing ? (
                          <input
                            type="number"
                            step="0.01"
                            className="inline-input narrow"
                            value={editForm.cgpa}
                            onChange={(e) => setEditForm({ ...editForm, cgpa: e.target.value })}
                          />
                        ) : (
                          <strong>{s.cgpa}</strong>
                        )}
                      </td>

                      {/* Category */}
                      <td>
                        {isEditing ? (
                          <select
                            className="inline-select"
                            value={editForm.category}
                            onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                          >
                            <option value="General">General</option>
                            <option value="OBC">OBC</option>
                            <option value="SC">SC</option>
                            <option value="ST">ST</option>
                            <option value="EWS">EWS</option>
                          </select>
                        ) : (
                          <span className="cat-pill">{s.category}</span>
                        )}
                      </td>

                      {/* Distance */}
                      <td>
                        {isEditing ? (
                          <input
                            type="number"
                            className="inline-input narrow"
                            value={editForm.distance_km}
                            onChange={(e) => setEditForm({ ...editForm, distance_km: e.target.value })}
                          />
                        ) : (
                          `${s.distance_km} km`
                        )}
                      </td>

                      {/* Special Needs */}
                      <td>
                        {isEditing ? (
                          <input
                            type="checkbox"
                            checked={editForm.special_needs === 1}
                            onChange={(e) =>
                              setEditForm({ ...editForm, special_needs: e.target.checked ? 1 : 0 })
                            }
                          />
                        ) : s.special_needs === 1 ? (
                          <span className="tag-pwd">PwD</span>
                        ) : (
                          'No'
                        )}
                      </td>

                      {/* Allocated Room */}
                      <td>
                        {isEditing ? (
                          <input
                            type="text"
                            placeholder="e.g. R_B_001"
                            className="inline-input"
                            value={editForm.allocated_room_id}
                            onChange={(e) => setEditForm({ ...editForm, allocated_room_id: e.target.value })}
                          />
                        ) : s.allocated_room_id ? (
                          <span className="room-badge">{s.allocated_room_id}</span>
                        ) : (
                          <span className="text-muted">Unallocated</span>
                        )}
                      </td>

                      {/* Actions */}
                      <td>
                        {isEditing ? (
                          <div className="btn-group-inline">
                            <button className="btn-action-save" onClick={() => saveEdit(s.student_id)}>
                              Save
                            </button>
                            <button className="btn-action-cancel" onClick={() => setEditingId(null)}>
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <div className="btn-group-inline">
                            <button className="btn-action-edit" onClick={() => startEdit(s)}>
                              Edit
                            </button>
                            <button className="btn-action-delete" onClick={() => handleDelete(s.student_id)}>
                              Delete
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="pagination-bar">
          <button
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
            className="btn-page"
          >
            ← Previous
          </button>
          <span>Page {page} of {totalPages}</span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
            className="btn-page"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
