# StarkGrid – Product Requirements Document (PRD)
**Version:** 0.1
**Product Type:** Web & Mobile (Map-First Dashboard)
**Domain:** Climate Intelligence, Renewable Energy, Geospatial Analytics

---

## 0. Product Vision

**StarkGrid** is a map-first web and mobile application for **climate-aware renewable energy planning**.
It enables users to analyze **energy potential, climate risk, and ecological impact together**, rather than in isolation.

**Core Principle**
> Every energy decision should be evaluated against climate, ecology, and resilience constraints.

---

## 1. Entry Screen – Authentication / Landing

### Purpose
- Establish trust and context
- Gate advanced analysis features

### User Types
- Guest (read-only, demo layers)
- Analyst / Researcher
- Government / NGO / Energy Planner

### UI Elements
- App name + tagline
- “Explore Map (Demo)”
- “Sign In / Create Account”

### Functional Requirements
- Guest mode: limited layers, no export
- Authenticated users: save projects, export analyses

---

## 2. Home Screen – Global Dashboard

### Purpose
Provide a high-level overview before deep map exploration.

### Layout
- Region / Country selector
- Mini overview map
- KPI cards

### Key KPIs
- Forest cover (%)
- Annual forest loss (last 5 years)
- Estimated wind potential zones
- Estimated hydro catchments
- Climate risk indicators (optional)

### Actions
- Open Map
- Create New Analysis
- Resume Project

---

## 3. Main Screen – Map Workspace (Core Screen)

### Purpose
Primary interaction surface for analysis.

### Layout

--------------------------------------------------
| Top Bar: Project | Export | Settings           |
--------------------------------------------------
| Layers Panel  |        Map Canvas              |
|               |                                |
|               |                                |
--------------------------------------------------
| Analysis Panel (Contextual, collapsible)       |
--------------------------------------------------

### Functional Requirements
- Pan, zoom, search
- Draw polygons / grids
- Toggle multiple layers
- Real-time statistics update

---

## 4. Layers Panel – Feature Selection

### Purpose
Enable feature-driven geospatial analysis.

### Layer Categories

#### A. Climate & Nature
- Forest Density
- Forest Loss / Gain
- Vegetation Health
- Protected Areas

#### B. Energy Potential
- Wind Potential
- Hydro Potential
- Solar (future)

#### C. Constraints
- Slope
- Elevation
- Distance to transmission grid
- Urban / settlement mask

### Functional Requirements
- Layer on/off toggle
- Opacity slider
- Auto legend
- Metadata display (source, resolution, update frequency)

---

## 5. Feature Module – Forest Density Analysis

### Definition (MVP)
Canopy cover percentage per grid cell (30m–100m resolution).

### Visualization
- Heatmap (0–100% canopy cover)
- Color legend
- Density threshold slider

### Analysis Panel
- Mean canopy cover (selected area)
- Area by density class
- Forest fragmentation metrics (v2)
- Change over time (loss / gain)

### User Actions
- Draw analysis area
- Mark as “Protected / Avoid”
- Export statistics

### Climate Impact Rationale
High-density forests represent major carbon stocks and biodiversity zones.
Avoiding these areas reduces emissions, ecosystem loss, and climate risk.

---

## 6. Feature Module – Wind Potential Mapping

### Objective
Identify suitable locations for wind power plants.

### Visualized Metrics
- Mean wind speed at hub height
- Seasonal variability

### UI Controls
- Height selector (80m / 100m / 120m)
- Time aggregation (annual / seasonal)

### Analysis Panel
- Mean wind speed
- Wind class (poor → excellent)
- Overlap with forest & protected areas
- Distance to grid infrastructure

### Suitability Score (Concept)

Wind Score =
+ normalized wind speed
– forest density penalty
– protected area penalty
– slope penalty

### Output
- Ranked candidate zones
- Suitability label (High / Medium / Low)

---

## 7. Feature Module – Hydro Power Screening

### Objective
Screen potential hydro (run-of-river) sites.

### Visualized Layers
- River networks
- Flow accumulation
- Elevation / head proxy

### UI Components
- River thickness = flow accumulation
- Clickable river segments
- Elevation profile preview

### Analysis Panel
- Estimated head (m)
- Catchment area (km²)
- Seasonal sensitivity (wet vs dry)
- Forest overlap warning

### Output
- Candidate hydro sites
- Climate resilience indicator

---

## 8. Multi-Feature Overlay – Nature-Positive Siting

### Purpose
Core StarkGrid differentiator.

### Inputs
- Forest Density
- Wind or Hydro Potential
- Constraints layers

### System Output
- Composite suitability index
- Highlighted zones with high energy potential and low climate impact

### UI
- Composite heatmap
- Explanation panel:
  - Why a site scores high
  - Key trade-offs and risks

---

## 9. Analysis Summary Screen

### Purpose
Decision-ready outputs for planners and stakeholders.

### Contents
- Map snapshot
- Key metrics (energy, forest, climate risk)
- Assumptions & methodology
- Data sources
- Confidence level

### Export Options
- PDF (policy / proposal ready)
- CSV (numerical data)
- GeoJSON (GIS integration)

---

## 10. Project Management Screen

### Purpose
Support real-world planning workflows.

### Features
- Saved projects
- Versioned analyses
- Notes and annotations
- Team collaboration (future)

---

## 11. Settings & Transparency Screen

### Purpose
Build credibility and trust.

### Contents
- Data sources
- Update frequencies
- Known limitations
- Methodology summaries

---

## Strategic Value of StarkGrid

- Integrates ML, geospatial analytics, climate science, and energy planning
- Encodes climate and ecological trade-offs directly into decisions
- Highly relevant for Indonesia and Global South contexts
- Strong foundation for research grants, policy tools, and commercial platforms