import React, { useState, useEffect, useRef } from 'react';
import { getAudit, getExportAllocationUrl } from './api';
import KpiCards from './components/KpiCards';
import PolicySidebar from './components/PolicySidebar';
import PriorityScatter from './components/PriorityScatter';
import BiasBars from './components/BiasBars';
import ViolationsTable from './components/ViolationsTable';
import StudentDetailDrawer from './components/StudentDetailDrawer';
import StudentsTab from './components/StudentsTab';
import RoomsTab from './components/RoomsTab';
import StudentLookupTab from './components/StudentLookupTab';
import './App.css';

const DEFAULT_WEIGHTS = {
  w_cgpa: 0.35,
  w_distance: 0.20,
  w_year: 0.20,
  w_category: 0.10,
  w_special_needs: 0.15,
  w_room_mess: 0.60,
  w_room_floor: 0.40,
  tolerance_pct: 10,
};

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuditing, setIsAuditing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedStudentId, setSelectedStudentId] = useState(null);

  const debounceTimer = useRef(null);

  useEffect(() => {
    fetchAudit(DEFAULT_WEIGHTS, true);
  }, []);

  const fetchAudit = async (currentWeights, isInitial = false) => {
    if (isInitial) setLoading(true);
    else setIsAuditing(true);
    setError(null);

    try {
      const data = await getAudit(currentWeights);
      setAuditData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setIsAuditing(false);
    }
  };

  const handleWeightsChange = (newWeights) => {
    setWeights(newWeights);
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    debounceTimer.current = setTimeout(() => {
      fetchAudit(newWeights, false);
    }, 300);
  };

  const handleResetWeights = () => {
    setWeights(DEFAULT_WEIGHTS);
    fetchAudit(DEFAULT_WEIGHTS, false);
  };

  // Called when a student or room is created, edited, or deleted in the DB tabs
  const handleDataChanged = () => {
    fetchAudit(weights, false);
  };

  return (
    <div className="h-app">
      {/* Top Navigation Bar */}
      <header className="h-navbar">
        <div className="nav-brand">
          <span className="brand-badge">COEP HRAFA</span>
          <h2>Hostel Room Allocation Fairness Auditor</h2>
        </div>

        <div className="nav-center">
          <button
            className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`nav-tab ${activeTab === 'students' ? 'active' : ''}`}
            onClick={() => setActiveTab('students')}
          >
            Students
          </button>
          <button
            className={`nav-tab ${activeTab === 'rooms' ? 'active' : ''}`}
            onClick={() => setActiveTab('rooms')}
          >
            Rooms
          </button>
          <button
            className={`nav-tab ${activeTab === 'lookup' ? 'active' : ''}`}
            onClick={() => setActiveTab('lookup')}
          >
            Student Lookup
          </button>
        </div>

        <div className="nav-actions">
          <a
            href={getExportAllocationUrl()}
            download="corrected_allocation.csv"
            className="btn-export"
            title="Download mathematically fair corrected allocation as CSV"
          >
            Export Corrected CSV
          </a>
        </div>
      </header>

      {/* Main View Area */}
      {loading ? (
        <div className="app-loader">
          <div className="spinner"></div>
          <p>Running initial fairness audit on student cohort...</p>
        </div>
      ) : error ? (
        <div className="app-error-banner">
          <h3>Backend Audit Error</h3>
          <p>{error}</p>
          <button onClick={() => fetchAudit(weights, true)} className="btn-primary mt-3">
            Retry Connection
          </button>
        </div>
      ) : (
        <main className="h-layout">
          {/* TAB 1: Main Visual Analytics Dashboard */}
          {activeTab === 'dashboard' && (
            <>
              {/* Left Column: Sliders */}
              <PolicySidebar
                weights={weights}
                onChange={handleWeightsChange}
                onReset={handleResetWeights}
                isAuditing={isAuditing}
              />

              {/* Right Column: Visualization Stack */}
              <section className="h-content">
                <KpiCards summary={auditData?.summary} />
                <PriorityScatter
                  students={auditData?.students || []}
                  onSelectStudent={(id) => setSelectedStudentId(id)}
                />
                <BiasBars
                  groupStats={auditData?.group_stats || {}}
                  tolerance={auditData?.summary?.tolerance_used || 15}
                />
                <ViolationsTable
                  pairs={auditData?.displacement_pairs || []}
                  onSelectStudent={(id) => setSelectedStudentId(id)}
                />
              </section>
            </>
          )}

          {/* TAB 2: Students Database Management */}
          {activeTab === 'students' && (
            <section className="h-content full-width">
              <StudentsTab onDataChanged={handleDataChanged} />
            </section>
          )}

          {/* TAB 3: Rooms Database Management */}
          {activeTab === 'rooms' && (
            <section className="h-content full-width">
              <RoomsTab onDataChanged={handleDataChanged} />
            </section>
          )}

          {/* TAB 4: Student Lookup Tab */}
          {activeTab === 'lookup' && (
            <section className="h-content full-width">
              <StudentLookupTab />
            </section>
          )}
        </main>
      )}

      {/* Explainability Side Drawer */}
      {selectedStudentId && (
        <StudentDetailDrawer
          studentId={selectedStudentId}
          onClose={() => setSelectedStudentId(null)}
        />
      )}
    </div>
  );
}
