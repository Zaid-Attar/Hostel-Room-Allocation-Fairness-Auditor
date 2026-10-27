# Hostel Room Allocation Fairness Auditor (HRAFA)

**Academic Mini-Project for Database Management Systems (DBMS) & Data Visualization (DV)**  
**COEP Technological University (A.Y. 2025-26)**  

### Team Members & Module Distribution:

| Member | MIS ID | Project Part | Core Responsibilities |
| :--- | :--- | :--- | :--- |
| **Zaid Attar** | 612415015 | **Part 1: Relational Database & DBMS Core** | 3NF Schema design, DDL constraints (`UNIQUE(room_id)`), ACID transaction handling, and SQL CRUD queries. |
| **Arpit Tiwari** | 612415012 | **Part 2: Fairness Audit & Statistical Engine** | Multi-criteria priority scoring, room ranking, Spearman rank correlation ($\rho$), and line-jumping anomaly detection. |
| **Trushant Chilvery** | 612415040 | **Part 3: FastAPI Backend & REST API Service** | REST API endpoints, Pydantic request validation, live query overrides, SQLite fallback, and CSV export. |
| **Aryan Bhure** | 612415030 | **Part 4: Frontend & Visual Analytics Dashboard** | React dashboard, Recharts scatter plot with ideal line, demographic bias breakdown, policy sliders, and explainability drawer. |

---

### Project Architecture (4 Core Parts):
1. **Part 1: Relational Database Layer (DBMS)** — 5 normalized tables in 3NF, declarative integrity constraints, foreign keys (`ON DELETE CASCADE`), and ACID transactional consistency.
2. **Part 2: Fairness Audit & Statistical Engine** — Algorithmic multi-criteria priority scoring, room ranking, PwD accessibility checks, and Spearman rank correlation ($\rho$).
3. **Part 3: REST API Service (FastAPI)** — High-performance REST endpoints for live dynamic auditing, individual explainability, and database CRUD operations.
4. **Part 4: Visual Analytics Dashboard (React + Recharts)** — Real-time interactive UI with policy sliders, hero scatter plot, demographic bias breakdown, and line-jumping accountability table.


## 1. Overview & Problem Statement

Institutional hostel room allocation algorithms frequently face transparency and fairness challenges. The **Hostel Room Allocation Fairness Auditor (HRAFA)** is an algorithmic auditing and visual analytics system that evaluates official hostel bed allocations against statutory institutional policies and reservation guidelines.

The system ingests three standard datasets:
- **`students.csv`**: Demographic, merit (CGPA), seniority, distance, category, and disability status.
- **`rooms.csv`**: Hostel block, gender pool, floor accessibility, and mess distance.
- **`allocation.csv`**: The actual institutional bed allocation record.

The auditor reconstructs the **ideal fair allocation** using configurable multi-criteria weighting, compares it against the actual allocation, flags anomalies (priority inversions, line-jumping, and upper-floor accessibility breaches), and renders findings in an interactive **React + Recharts** dashboard.

> **Important Academic Disclosure:** All student records and room records in the default dataset are **synthetically generated** (`seed=42`) with deliberate planted edge-case anomalies (~8% rank gap swaps, 3 upper-floor PwD breaches, 2 unallocated applicants, and an OBC demographic disparity) to demonstrate audit sensitivity. Policy weights represent configurable example institutional rules.

---

## 2. System Architecture & Tech Stack

- **Backend:** Python 3.11+, FastAPI (REST API), SQLAlchemy (ORM/DDL execution), PyMySQL, Pandas, NumPy, SciPy (Spearman Rank Correlation), and Pytest.
- **Database (DBMS):** MySQL 8 (configured via `DATABASE_URL` in `.env`, with automatic zero-install SQLite fallback `hostel_auditor.db` for instant local evaluation).
- **Frontend & Visual Analytics:** React with Vite, Recharts (ScatterChart, horizontal BarChart), and custom Vanilla CSS (minimal dark-mode design system with no heavy UI framework dependencies).
- **Audit Metric:** Global Spearman Rank Correlation ($\rho$) between composite student priority and allocated room quality, scaled to 0–100.

---

## 3. Relational Database Schema (5 Core Tables)

Defined in [`backend/scripts/schema.sql`](file:///c:/Users/diaza/Desktop/Code/Hostel-Room-Allocation-Fairness-Auditor/backend/scripts/schema.sql):
1. **`students`**: `student_id` (PK), `name`, `gender`, `year`, `cgpa`, `category`, `distance_km`, `special_needs`.
2. **`rooms`**: `room_id` (PK), `hostel`, `gender`, `floor`, `mess_distance_m`, `accessible`.
3. **`allocations`**: `student_id` (PK, FK), `room_id` (Unique, FK).
4. **`policy_rules`**: `rule_key` (PK), `value`.
5. **`audit_results`**: `student_id` (PK), `priority_score`, `expected_room_id`, `actual_room_id`, `deviation`, `status`, `hard_rule_violation`, `audited_at`.

---

## 4. Key Auditing Logic (`backend/app/audit.py`)

1. **Composite Priority Score:** Weighted normalized combination of CGPA ($35\%$), Home Distance ($20\%$), Seniority ($20\%$), Category Reservation Bonus ($10\%$), and Special Needs ($15\%$).
2. **Room Quality Score:** Normalized quality based on mess proximity ($60\%$) and ground-floor accessibility ($40\%$).
3. **Gender Pools:** Males (Boys Hostel) and Females (Girls Hostel) are partitioned into separate independent ranking pools.
4. **Statutory Expected Allocation:** Special-needs students are guaranteed priority access to ground-floor accessible rooms. Remaining students are assigned descending room quality strictly by priority rank.
5. **Disparity Deviations & Status:**
   - $\text{Deviation} = \text{Actual Room Rank} - \text{Expected Room Rank}$.
   - Evaluated against a configurable tolerance window ($\pm 10\%$ of rooms):
     - `FAIR`: $|\text{Deviation}| \le \text{Tolerance}$
     - `OVER_FAVORED`: $\text{Deviation} < -\text{Tolerance}$ (Beneficiary of line-jumping)
     - `UNDER_SERVED`: $\text{Deviation} > \text{Tolerance}$ (Deprived merit victim)
     - `UNALLOCATED`: Entitled applicant denied accommodation
6. **Hard Accessibility Check:** Any special-needs applicant placed on an upper non-accessible floor (Floor $>0$) triggers `SPECIAL_NEEDS_NOT_ACCESSIBLE` regardless of deviation.
7. **Displacement Accountability Pairs:** Directly matches each deprived student with the lower-priority student who received their room.

---

## 5. Quickstart & Setup Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Step 1: Clone and Configure Environment
```bash
git clone https://github.com/Zaid-Attar/Hostel-Room-Allocation-Fairness-Auditor.git
cd Hostel-Room-Allocation-Fairness-Auditor

# Copy environment template
cp .env.example .env
```
*(Optional: If connecting to an external MySQL server, set `DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hostel_auditor` in `.env`)*

---

### Step 2: Install Backend Dependencies & Populate Database
```bash
# Install Python requirements
pip install -r backend/requirements.txt

# Run validation checks & load database tables
python backend/scripts/load_csv.py
```

---

### Step 3: Run Automated Test Suite
```bash
python -m pytest backend/tests/ -v
```
*(Runs 14 unit and integration tests verifying perfect allocations, top/bottom swaps, hard PwD rules, unallocated handling, and API routes)*

---

### Step 4: Launch Backend API Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- Backend Health Check: `http://localhost:8000/health`

---

### Step 5: Launch Frontend React Dashboard
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at **`http://localhost:5173`**.

---

## 6. Dashboard Capabilities

- **Dashboard Tab:**
  - **Live Sliders:** Adjust policy weights in real time; the fairness score ($\rho$) and scatter plot recompute automatically.
  - **KPI Row:** Live fairness score, violation rate, total allocations, and compliance rate.
  - **Hero Scatter Plot:** Recharts scatter chart with diagonal ideal reference line ($y = x$) and distinct series for Fair, Over-Favored, and Under-Served students.
  - **Demographic Bias Breakdown:** Bar chart toggling between average deviation and percentage flagged across Category, Year, Distance Band, and Gender.
  - **Accountability Table:** Side-by-side evidence of line-jumping pairs sorted by priority gap.
  - **Explainability Drawer:** Click any point or student to inspect their factor-by-factor breakdown and plain-English grievance finding.
- **Students Tab:** Complete database management table with category/gender/year filters, add student form, inline edit, and delete.
- **Rooms Tab:** Bed management table with hostel/floor/accessible filters, add room form, inline edit, and delete.
- **Student Lookup Tab:** Search any student ID to inspect their entitled room vs actual room.
- **Export Corrected Allocation CSV:** One-click download button in the navigation bar to export the mathematically fair allocation.

---

## 7. Assumptions & Design Decisions
1. **Separate Gender Pools:** Hostel allocations for male and female applicants are processed in independent pools since hostel buildings are segregated by gender.
2. **Bed Unit Allocation:** Each entry in `rooms.csv` represents a single allocatable bed space.
3. **Database Portability:** Implements pure SQLAlchemy parameterized queries compatible with both MySQL 8 and SQLite, allowing zero-friction demonstrations in any lab evaluation environment.
