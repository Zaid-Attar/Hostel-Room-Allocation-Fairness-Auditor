/**
 * API client for Hostel Room Allocation Fairness Auditor (HRAFA)
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function getPolicy() {
  const res = await fetch(`${BASE_URL}/policy`);
  if (!res.ok) throw new Error(`Failed to fetch policy: ${res.statusText}`);
  return res.json();
}

export async function getAudit(weights = {}) {
  const params = new URLSearchParams();
  for (const [key, val] of Object.entries(weights)) {
    if (val !== undefined && val !== null) {
      params.append(key, val);
    }
  }
  const queryString = params.toString() ? `?${params.toString()}` : '';
  const res = await fetch(`${BASE_URL}/audit${queryString}`);
  if (!res.ok) throw new Error(`Audit failed: ${res.statusText}`);
  return res.json();
}

export async function getStudentExplanation(studentId) {
  const res = await fetch(`${BASE_URL}/audit/student/${encodeURIComponent(studentId)}`);
  if (!res.ok) throw new Error(`Failed to fetch student explanation: ${res.statusText}`);
  return res.json();
}

export function getExportAllocationUrl() {
  return `${BASE_URL}/export/corrected-allocation.csv`;
}

// ---------------------------------------------------------------------------
// Students CRUD
// ---------------------------------------------------------------------------
export async function getStudents(params = {}) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') {
      qs.append(k, v);
    }
  }
  const query = qs.toString() ? `?${qs.toString()}` : '';
  const res = await fetch(`${BASE_URL}/students${query}`);
  if (!res.ok) throw new Error(`Failed to fetch students: ${res.statusText}`);
  return res.json();
}

export async function createStudent(data) {
  const res = await fetch(`${BASE_URL}/students`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to create student: ${res.statusText}`);
  }
  return res.json();
}

export async function updateStudent(studentId, data) {
  const res = await fetch(`${BASE_URL}/students/${encodeURIComponent(studentId)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to update student: ${res.statusText}`);
  }
  return res.json();
}

export async function deleteStudent(studentId) {
  const res = await fetch(`${BASE_URL}/students/${encodeURIComponent(studentId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete student: ${res.statusText}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Rooms CRUD
// ---------------------------------------------------------------------------
export async function getRooms(params = {}) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') {
      qs.append(k, v);
    }
  }
  const query = qs.toString() ? `?${qs.toString()}` : '';
  const res = await fetch(`${BASE_URL}/rooms${query}`);
  if (!res.ok) throw new Error(`Failed to fetch rooms: ${res.statusText}`);
  return res.json();
}

export async function createRoom(data) {
  const res = await fetch(`${BASE_URL}/rooms`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to create room: ${res.statusText}`);
  }
  return res.json();
}

export async function updateRoom(roomId, data) {
  const res = await fetch(`${BASE_URL}/rooms/${encodeURIComponent(roomId)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to update room: ${res.statusText}`);
  }
  return res.json();
}

export async function deleteRoom(roomId) {
  const res = await fetch(`${BASE_URL}/rooms/${encodeURIComponent(roomId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete room: ${res.statusText}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Allocations CRUD
// ---------------------------------------------------------------------------
export async function updateAllocation(studentId, roomId) {
  const res = await fetch(`${BASE_URL}/allocations/${encodeURIComponent(studentId)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ room_id: roomId || null }),
  });
  if (!res.ok) throw new Error(`Failed to update allocation: ${res.statusText}`);
  return res.json();
}

export default {
  checkHealth,
  getPolicy,
  getAudit,
  getStudentExplanation,
  getExportAllocationUrl,
  getStudents,
  createStudent,
  updateStudent,
  deleteStudent,
  getRooms,
  createRoom,
  updateRoom,
  deleteRoom,
  updateAllocation,
};
