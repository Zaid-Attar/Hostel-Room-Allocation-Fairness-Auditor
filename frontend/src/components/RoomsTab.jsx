import React, { useState, useEffect } from 'react';
import { getRooms, createRoom, updateRoom, deleteRoom } from '../api';

export default function RoomsTab({ onDataChanged }) {
  const [rooms, setRooms] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters & Pagination
  const [hostel, setHostel] = useState('');
  const [gender, setGender] = useState('');
  const [floor, setFloor] = useState('');
  const [accessible, setAccessible] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Add Room Form
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRoom, setNewRoom] = useState({
    room_id: '',
    hostel: 'Boys Block Alpha',
    gender: 'M',
    floor: 0,
    mess_distance_m: 50,
    accessible: 1,
  });

  // Inline Editing
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    fetchRoomList();
  }, [hostel, gender, floor, accessible, search, page]);

  const fetchRoomList = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getRooms({
        hostel,
        gender,
        floor: floor !== '' ? parseInt(floor) : undefined,
        accessible: accessible !== '' ? parseInt(accessible) : undefined,
        search,
        page,
        page_size: pageSize,
      });
      setRooms(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRoom = async (e) => {
    e.preventDefault();
    try {
      await createRoom({
        ...newRoom,
        floor: parseInt(newRoom.floor),
        mess_distance_m: parseInt(newRoom.mess_distance_m),
        accessible: parseInt(newRoom.accessible),
      });
      setShowAddForm(false);
      setNewRoom({
        room_id: '',
        hostel: 'Boys Block Alpha',
        gender: 'M',
        floor: 0,
        mess_distance_m: 50,
        accessible: 1,
      });
      fetchRoomList();
      if (onDataChanged) onDataChanged();
    } catch (err) {
      alert(`Error creating room: ${err.message}`);
    }
  };

  const startEdit = (r) => {
    setEditingId(r.room_id);
    setEditForm({
      hostel: r.hostel,
      floor: r.floor,
      mess_distance_m: r.mess_distance_m,
      accessible: r.accessible,
    });
  };

  const saveEdit = async (roomId) => {
    try {
      await updateRoom(roomId, {
        hostel: editForm.hostel,
        floor: parseInt(editForm.floor),
        mess_distance_m: parseInt(editForm.mess_distance_m),
        accessible: parseInt(editForm.accessible),
      });
      setEditingId(null);
      fetchRoomList();
      if (onDataChanged) onDataChanged();
    } catch (err) {
      alert(`Error updating room: ${err.message}`);
    }
  };

  const handleDelete = async (roomId) => {
    if (!window.confirm(`Are you sure you want to delete room ${roomId}?`)) return;
    try {
      await deleteRoom(roomId);
      fetchRoomList();
      if (onDataChanged) onDataChanged();
    } catch (err) {
      alert(`Error deleting room: ${err.message}`);
    }
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="tab-container">
      {/* Header */}
      <div className="tab-header-card">
        <div className="tab-title-group">
          <h3>Hostel Bed Capacity Records</h3>
          <p className="chart-desc">
            Manage rooms, floors, mess proximity, and PwD ground-floor accessibility flags.
          </p>
        </div>

        <button
          className="btn-primary"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Cancel' : '+ Add New Room'}
        </button>
      </div>

      {/* Add Room Modal Form */}
      {showAddForm && (
        <form onSubmit={handleCreateRoom} className="add-record-card">
          <h4>Register New Bed / Room</h4>
          <div className="form-grid">
            <div className="form-group">
              <label>Room ID (e.g. R_B_201)</label>
              <input
                type="text"
                required
                value={newRoom.room_id}
                onChange={(e) => setNewRoom({ ...newRoom, room_id: e.target.value })}
                placeholder="R_B_201"
              />
            </div>
            <div className="form-group">
              <label>Hostel Block</label>
              <input
                type="text"
                required
                value={newRoom.hostel}
                onChange={(e) => setNewRoom({ ...newRoom, hostel: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Gender Assigned</label>
              <select
                value={newRoom.gender}
                onChange={(e) => setNewRoom({ ...newRoom, gender: e.target.value })}
              >
                <option value="M">Boys (M)</option>
                <option value="F">Girls (F)</option>
              </select>
            </div>
            <div className="form-group">
              <label>Floor (0 is Ground)</label>
              <input
                type="number"
                min="0"
                max="10"
                required
                value={newRoom.floor}
                onChange={(e) => {
                  const fl = parseInt(e.target.value) || 0;
                  setNewRoom({
                    ...newRoom,
                    floor: fl,
                    accessible: fl === 0 ? 1 : 0,
                  });
                }}
              />
            </div>
            <div className="form-group">
              <label>Mess Distance (meters)</label>
              <input
                type="number"
                min="10"
                max="1000"
                required
                value={newRoom.mess_distance_m}
                onChange={(e) => setNewRoom({ ...newRoom, mess_distance_m: e.target.value })}
              />
            </div>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={newRoom.accessible === 1}
                  onChange={(e) =>
                    setNewRoom({ ...newRoom, accessible: e.target.checked ? 1 : 0 })
                  }
                />
                {' '}Accessible (Ground Floor)
              </label>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">Save Room</button>
            <button type="button" className="btn-secondary" onClick={() => setShowAddForm(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Filter Row */}
      <div className="table-controls-row">
        <div className="filter-group-inline">
          <label>Hostel:</label>
          <select value={hostel} onChange={(e) => { setHostel(e.target.value); setPage(1); }}>
            <option value="">All Hostels</option>
            <option value="Boys Block Alpha">Boys Block Alpha</option>
            <option value="Girls Block Beta">Girls Block Beta</option>
          </select>
        </div>

        <div className="filter-group-inline">
          <label>Gender:</label>
          <select value={gender} onChange={(e) => { setGender(e.target.value); setPage(1); }}>
            <option value="">All Genders</option>
            <option value="M">Boys (M)</option>
            <option value="F">Girls (F)</option>
          </select>
        </div>

        <div className="filter-group-inline">
          <label>Floor:</label>
          <select value={floor} onChange={(e) => { setFloor(e.target.value); setPage(1); }}>
            <option value="">All Floors</option>
            <option value="0">Ground (0)</option>
            <option value="1">Floor 1</option>
            <option value="2">Floor 2</option>
            <option value="3">Floor 3</option>
            <option value="4">Floor 4</option>
          </select>
        </div>

        <div className="filter-group-inline">
          <label>Accessibility:</label>
          <select value={accessible} onChange={(e) => { setAccessible(e.target.value); setPage(1); }}>
            <option value="">All</option>
            <option value="1">Accessible Only</option>
            <option value="0">Standard Upper</option>
          </select>
        </div>

        <input
          type="text"
          className="search-input"
          placeholder="Search room ID..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />

        <span className="count-tag">Showing {rooms.length} of {total} rooms</span>
      </div>

      {/* Table */}
      <div className="table-card">
        {loading ? (
          <div className="text-center py-4 text-muted">Loading rooms...</div>
        ) : error ? (
          <div className="text-center py-4 text-bad">{error}</div>
        ) : (
          <div className="table-responsive">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Room ID</th>
                  <th>Hostel Block</th>
                  <th>Gender</th>
                  <th>Floor</th>
                  <th>Mess Distance</th>
                  <th>Accessible</th>
                  <th>Current Occupant</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rooms.map((r) => {
                  const isEditing = editingId === r.room_id;
                  return (
                    <tr key={r.room_id}>
                      <td><strong>{r.room_id}</strong></td>
                      <td>
                        {isEditing ? (
                          <input
                            type="text"
                            className="inline-input"
                            value={editForm.hostel}
                            onChange={(e) => setEditForm({ ...editForm, hostel: e.target.value })}
                          />
                        ) : (
                          r.hostel
                        )}
                      </td>
                      <td>{r.gender}</td>
                      <td>
                        {isEditing ? (
                          <input
                            type="number"
                            min="0"
                            className="inline-input narrow"
                            value={editForm.floor}
                            onChange={(e) => setEditForm({ ...editForm, floor: e.target.value })}
                          />
                        ) : (
                          r.floor === 0 ? 'Ground' : `Floor ${r.floor}`
                        )}
                      </td>
                      <td>
                        {isEditing ? (
                          <input
                            type="number"
                            min="0"
                            className="inline-input narrow"
                            value={editForm.mess_distance_m}
                            onChange={(e) => setEditForm({ ...editForm, mess_distance_m: e.target.value })}
                          />
                        ) : (
                          `${r.mess_distance_m} m`
                        )}
                      </td>
                      <td>
                        {isEditing ? (
                          <input
                            type="checkbox"
                            checked={editForm.accessible === 1}
                            onChange={(e) =>
                              setEditForm({ ...editForm, accessible: e.target.checked ? 1 : 0 })
                            }
                          />
                        ) : r.accessible === 1 ? (
                          <span className="tag-pwd">Accessible</span>
                        ) : (
                          'Standard'
                        )}
                      </td>
                      <td>
                        {r.allocated_student_id ? (
                          <span className="room-badge">{r.allocated_student_id}</span>
                        ) : (
                          <span className="text-muted">Vacant</span>
                        )}
                      </td>
                      <td>
                        {isEditing ? (
                          <div className="btn-group-inline">
                            <button className="btn-action-save" onClick={() => saveEdit(r.room_id)}>
                              Save
                            </button>
                            <button className="btn-action-cancel" onClick={() => setEditingId(null)}>
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <div className="btn-group-inline">
                            <button className="btn-action-edit" onClick={() => startEdit(r)}>
                              Edit
                            </button>
                            <button className="btn-action-delete" onClick={() => handleDelete(r.room_id)}>
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
