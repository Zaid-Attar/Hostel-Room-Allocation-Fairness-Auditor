# Technology Stack Architecture
**Project:** Hostel Room Allocation Fairness Auditor  
**Focus Areas:** Database Management Systems (DBMS) & Data Visualization (DV)  
**Authors:** Zaid Attar, Arpit Tiwari, Trushant Chilvery, Aryan Bhure  

---

## 1. High-Level Technology Overview

To maximize academic rigor, demonstrate advanced database principles, and deliver a visual analytics dashboard, the system is designed with a **modular 3-tier architecture**:

```
┌────────────────────────────────────────────────────────────────────────┐
│               TIER 1: PRESENTATION & DATA VISUALIZATION                │
│   • HTML5 Semantic Structure         • Vanilla CSS3 Design System      │
│   • Modern ES6+ JavaScript           • Chart.js v4 (Canvas Charts)     │
│   • SVG & D3-style Data Encodings    • Interactive Cross-Filtering     │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │  HTTP / RESTful JSON APIs
┌──────────────────────────────────▼─────────────────────────────────────┐
│                 TIER 2: BACKEND & FAIRNESS ENGINE                      │
│   • Python 3 (FastAPI / Flask)       • Raw SQL Execution Engine        │
│   • Statistical Fairness Metrics     • Optimal Re-allocation Solver    │
│   • CORS-enabled API Endpoints       • Report Exporter (CSV / PDF)     │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │  ACID Transactions & Analytical Views
┌──────────────────────────────────▼─────────────────────────────────────┐
│                     TIER 3: DATABASE (DBMS)                            │
│   • PostgreSQL (Primary ORDBMS Engine) • pgAdmin & psql CLI Support   │
│   • PL/pgSQL Triggers & Procedures   • 3NF Relational Schema           │
│   • SQL Window Functions (RANK, etc) • Check & Referential Constraints │
│   • Portable ANSI-SQL Scripts        • SQLite Fallback for Zero-Setup  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tier-by-Tier Stack Breakdown & Justifications

### Tier 1: Database Management Systems (DBMS)

| Component | Choice | Academic & Technical Justification |
|---|---|---|
| **Database Engine** | **PostgreSQL** (Primary ORDBMS)<br>*(with SQLite fallback)* | **1. Academic Gold Standard:** PostgreSQL is the industry-standard Object-Relational DBMS widely favored in university DBMS curricula for its strict standards compliance and robust SQL features.<br>**2. Advanced PL/pgSQL Procedural Engine:** Native support for rich `PL/pgSQL` functions and triggers (`CREATE FUNCTION ... RETURNS TRIGGER AS $$ ... $$ LANGUAGE plpgsql;`).<br>**3. Complex Analytical Window Functions:** Native, highly optimized support for `DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)`.<br>**4. Enterprise Constraints:** Strict domain constraints (`CHECK`), custom ENUM types, and referential integrity (`ON DELETE CASCADE` / `ON DELETE RESTRICT`).<br>**5. Portable & Flexible:** Provides clean `.sql` scripts executable directly in `psql` or pgAdmin, alongside a zero-install SQLite fallback mode for quick offline demos. |
| **Relational Model** | **3rd Normal Form (3NF)** | Eliminates update, insertion, and deletion anomalies. Separate entities for `STUDENT`, `ROOM`, `POLICY_RULE`, `ALLOCATION`, `ALLOCATION_HISTORY`, `GRIEVANCE`, and `AUDIT_ANOMALY`. |
| **Advanced Features** | **PL/pgSQL Triggers & Window Functions** | • `trg_capacity_guard`: Enforces room capacity limits before insert/update.<br>• `trg_log_allocation_history`: Automatically logs all allocation changes to history.<br>• Window functions (`DENSE_RANK() OVER (PARTITION BY category ORDER BY merit_score DESC)`): Computes category-wise rankings directly inside the database engine. |
| **Query Strategy** | **Raw Parameterized SQL** | Instead of an opaque Object-Relational Mapper (ORM) that hides queries, the backend executes **raw, parameterized SQL queries**. This makes query performance, joins, subqueries, and `EXPLAIN ANALYZE` directly inspectable and defendable during lab evaluations. |

---

### Tier 2: Backend & Computation Layer

| Component | Choice | Academic & Technical Justification |
|---|---|---|
| **Programming Language** | **Python 3.10+** | Industry-standard language for data manipulation, mathematical formulations, and scientific auditing. Uses `psycopg2-binary` for robust PostgreSQL connections, with built-in `sqlite3` for zero-install fallback. |
| **Web API Framework** | **FastAPI** (or Flask) | • Lightweight, high-throughput asynchronous REST API.<br>• Automatically generates interactive OpenAPI/Swagger documentation at `/docs`, enabling evaluators to test individual SQL endpoints directly in the browser.<br>• Clean separation of concern: routes serve only pure JSON data to the frontend. |
| **Auditing & Fairness Engine** | **Custom Python Fairness Logic** | Computes mathematical disparity metrics: Disparate Impact Ratio, Priority Inversion Frequency, Demographic Parity Gap, and Institutional Fairness Score (0–100%). |
| **Optimization Solver** | **Algorithmic Re-allocator** | Implements a greedy/linear priority assignment algorithm that ingests the audited data, applies the strict policy criteria, and generates a mathematically optimal allocation for side-by-side comparison. |

---

### Tier 3: Frontend & Data Visualization (DV)

| Component | Choice | Academic & Technical Justification |
|---|---|---|
| **Core Web Tech** | **HTML5 & Vanilla Modern JavaScript (ES6+)** | Zero build step (`npm run build` not required), instant load times, clean native DOM manipulation. Uses native `fetch()` for API communication. |
| **Styling & Design System** | **Vanilla CSS3** | Custom dark-mode design system with CSS custom properties (variables), glassmorphic cards (`backdrop-filter`), smooth micro-transitions, and responsive flex/grid layouts. Avoids boilerplate utility libraries for total aesthetic control. |
| **Primary Charting Library** | **Chart.js v4** | Hardware-accelerated HTML5 Canvas charting engine. Supports dynamic responsive resizing, customizable tooltips, annotations, zoom plugins, and smooth animations. |
| **Specialized Visualizations** | **SVG & CSS Heatmap Engine** | • **Hostel Floor & Room Heatmap:** Custom SVG/CSS grid representing hostel blocks, floors, and individual rooms, colored by occupancy and anomaly severity.<br>• **Rank Inversion Ladder:** Custom slope chart connecting entitled policy ranks to actual allocated ranks to visualize line-jumping. |

---

## 3. Visualization Catalog & Chart Mapping

To satisfy the Data Visualization course objectives, every chart is mapped to a specific analytical question:

```
┌──────────────────────────────────────┬──────────────────────────────────────┐
│ Chart Type                           │ Analytical Purpose                   │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 1. Multi-Dimensional Scatter Plot    │ Quadrant analysis of CGPA vs.        │
│    (with custom quadrant shading)    │ Distance to immediately spot biased  │
│                                      │ allotments in low-merit quadrants.   │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 2. Grouped & Stacked Bar Chart       │ Mandated Quota % vs. Actual          │
│                                      │ Allocation % across categories       │
│                                      │ (General, OBC, SC, ST, EWS, PwD).    │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 3. Rank Inversion Bump / Slope Chart │ Maps entitled merit rank on the left │
│                                      │ to allocated rank on the right.      │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 4. Hostel Room & Floor Heatmap       │ 2D grid of hostel rooms colored by   │
│                                      │ occupancy, PwD accessibility, and    │
│                                      │ violation flags.                     │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 5. Grievance Distribution & Funnel   │ Analyzes student complaints and      │
│                                      │ correlates them with system-detected │
│                                      │ fairness anomalies.                  │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 6. Comparative Before-vs-After Radar │ Displays side-by-side metric deltas  │
│    & Metric Gauge Cards              │ (Fairness Index before vs. after     │
│                                      │ algorithmic correction).             │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 4. Why This Stack is Ideal for Project Viva & Evaluation

1. **Direct Visibility of SQL Concepts:**
   Evaluators test students on queries, triggers, views, and normalization. Because this stack uses raw SQL with analytical window functions rather than an ORM, team members can open any `.sql` file or run queries live in the terminal.
2. **Zero Setup & High Portability:**
   Anyone can run `python -m backend.app` and open `frontend/index.html` without running database servers, setting passwords, or troubleshooting node build pipelines.
3. **Rich Interactivity:**
   Evaluators can filter by year or category and immediately observe all charts, heatmaps, and metrics update in real-time.
4. **Reproducible Test Data:**
   The seed dataset includes specific, documented edge cases (e.g. high-CGPA waitlisted student vs. low-CGPA allocated student from the same category) so you can demonstrate the audit flag triggers live.
