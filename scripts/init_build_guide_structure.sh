#!/bin/bash
# =============================================================================
# OT Digital Twin — Build Guide v1.0 Structure Initializer
# i3 Technologies Ltd / GDC Kenya
# Author: Wisdom Kinoti
# Created: 28 March 2026
# =============================================================================
# Restructures repo to match Build Guide v1.0 (9-step enterprise spec).
# Preserves all existing working code. Creates placeholder files and manifests.
# Usage: bash scripts/init_build_guide_structure.sh
# Run from: Q:\bcs\ibm\EAAAIW @ IBM Research Lab Africa\OTDT\otdt\OTDT
# =============================================================================

set -e

# ─── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# ─── Helpers ──────────────────────────────────────────────────────────────────
step()    { echo -e "\n${BLUE}${BOLD}[$1] $2${NC}"; }
ok()      { echo -e "  ${GREEN}✔${NC}  $1"; }
warn()    { echo -e "  ${YELLOW}⚠${NC}  $1"; }
err()     { echo -e "  ${RED}✖${NC}  $1"; }
mkd()     { if [ ! -d "$1" ]; then mkdir -p "$1" && ok "Created $1"; else warn "Exists  $1"; fi; }
mkf()     { if [ ! -f "$1" ]; then cat > "$1"; ok "Created $1"; else warn "Skipped $1 (already exists)"; cat > /dev/null; fi; }

# ─── Guard: must run from project root ────────────────────────────────────────
if [ ! -f "docker-compose.yml" ] && [ ! -d "api" ] && [ ! -d "monte_carlo" ]; then
  err "Not in project root. cd to OTDT/ first."
  exit 1
fi

echo -e "\n${BOLD}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  OT Digital Twin — Build Guide v1.0 Structure Initializer${NC}"
echo -e "${BOLD}════════════════════════════════════════════════════════════════${NC}"
echo -e "  Root: $(pwd)"
echo -e "  Date: $(date '+%Y-%m-%d %H:%M:%S')"

# =============================================================================
# [1/6] VERIFY EXISTING WORKING CODE
# =============================================================================
step "1/6" "Verifying existing working code (must not be touched)"

for d in monte_carlo api sensor_simulator frontend; do
  if [ -d "$d" ]; then
    ok "$d/ — preserved"
  else
    warn "$d/ — NOT FOUND (expected existing code)"
  fi
done

# =============================================================================
# [2/6] CREATE DIRECTORY STRUCTURE
# =============================================================================
step "2/6" "Creating Build Guide directory structure"

# Step 1 — Infrastructure / TechZone
mkd "infrastructure/techzone"
mkd "infrastructure/terraform/ibm_cloud"

# Step 2 — Maximo
mkd "maximo/schemas"

# Step 3 — Unity XR
mkd "unity/GDC_Plant_Twin/Assets/Scripts"
mkd "unity/GDC_Plant_Twin/Assets/Scenes"
mkd "unity/GDC_Plant_Twin/Assets/Materials"
mkd "unity/GDC_Plant_Twin/Builds/WebGL"
mkd "unity/ThreeJS_Viewer"

# Steps 4 & 7 — ML
mkd "ml/lstm/notebooks"
mkd "ml/lstm/models"
mkd "ml/lstm/data"
mkd "ml/cnn_anomaly/notebooks"
mkd "ml/cnn_anomaly/models"

# Step 8 — Scheduler
mkd "scheduler"

# Step 9 — OpenShift
mkd "deployment/openshift/base"
mkd "deployment/openshift/overlays/dev"
mkd "deployment/openshift/overlays/prod"
mkd "deployment/docker"

# Datasets & Docs
mkd "datasets"
mkd "docs/architecture"
mkd "docs/api"
mkd "scripts"

# =============================================================================
# [3/6] CREATE PYTHON PLACEHOLDER FILES
# =============================================================================
step "3/6" "Creating Python placeholder files"

# ── maximo/__init__.py ───────────────────────────────────────────────────────
mkf "maximo/__init__.py" << 'PYEOF'
"""
Maximo MAS 9.1 Integration Module
Build Guide Step 2: Live data bridge between Maximo APM and Unity 3D model.

Provides:
- Asset hierarchy loading from datasets/GDC_Assets.xlsx
- REST API client for Maximo Monitor sensor data
- Automatic work order creation from scheduler
"""
__version__ = "0.1.0"
PYEOF

# ── maximo/asset_loader.py ───────────────────────────────────────────────────
mkf "maximo/asset_loader.py" << 'PYEOF'
"""Load GDC Kenya asset hierarchy from datasets/GDC_Assets.xlsx into Maximo.

Build Guide Step 2: Asset Hierarchy
- Loads 50 asset records from Excel
- Creates Sites → Systems → Equipment hierarchy
- Configures sensor data points (temp, pressure, vibration, flow, RPM)

SYNTHETIC DATA DISCLAIMER: All data is computer-generated. Not representative
of any real client operational data.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "asset_id", "asset_class", "description", "installation_date",
    "design_pressure_bar", "design_temp_c", "last_maintenance_date",
    "maintenance_interval_days", "replacement_cost_usd", "unity_object_name",
]

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "GDC_Assets.xlsx"


class AssetLoader:
    """Loads GDC Kenya asset hierarchy from Excel and pushes to Maximo."""

    def __init__(self, maximo_client=None):
        """
        Args:
            maximo_client: Authenticated MaximoWorkOrderClient or MaximoMonitorClient.
        """
        self.client = maximo_client
        self.assets: List[Dict[str, Any]] = []

    def load_from_excel(self, path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Read asset records from Excel.

        Args:
            path: Override default dataset path.

        Returns:
            List of asset dicts with all expected columns.

        Raises:
            FileNotFoundError: If dataset not present.
            ValueError: If required columns are missing.
        """
        # TODO: Implement per Build Guide Step 2
        # 1. pd.read_excel(path or DATASET_PATH)
        # 2. Validate EXPECTED_COLUMNS are present
        # 3. Coerce types (dates, floats)
        # 4. Populate self.assets
        raise NotImplementedError

    def push_to_maximo(self) -> Dict[str, int]:
        """Create asset records in Maximo via REST API.

        Returns:
            Dict with keys: created, skipped, failed
        """
        # TODO: Implement per Build Guide Step 2
        raise NotImplementedError
PYEOF

# ── maximo/monitor_client.py ─────────────────────────────────────────────────
mkf "maximo/monitor_client.py" << 'PYEOF'
"""REST API client for Maximo Monitor sensor data.

Provides HTTP bridge to Maximo MAS 9.1 Monitor module.
Build Guide Step 2: Live sensor data feed into Unity 3D model.

SYNTHETIC DATA DISCLAIMER: All data is computer-generated. Not representative
of any real client operational data.
"""
import logging
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MaximoMonitorClient:
    """Client for Maximo Monitor REST API."""

    def __init__(self, base_url: str, username: str, password: str):
        """
        Args:
            base_url: e.g. https://<your-maximo-host>/maximo
            username: Maximo login
            password: Maximo password
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session: Optional[requests.Session] = None

    def authenticate(self) -> None:
        """Establish authenticated session with Maximo."""
        # TODO: Implement per Build Guide Step 2
        raise NotImplementedError

    def get_latest_sensors(self, asset_id: str) -> Dict[str, float]:
        """Get latest sensor readings for an asset.

        Args:
            asset_id: Maximo asset ID (e.g. GDC-WP-007)

        Returns:
            Dict with keys: temperature_c, pressure_bar, vibration_mm_s,
                            flow_rate_kg_s, rotation_rpm
        """
        # TODO: Implement per Build Guide Step 2
        raise NotImplementedError

    def get_sensor_history(self, asset_id: str, hours: int = 24) -> List[Dict]:
        """Get historical sensor readings for trend analysis.

        Args:
            asset_id: Maximo asset ID
            hours: Lookback window in hours

        Returns:
            List of timestamped sensor dicts, oldest first
        """
        # TODO: Implement per Build Guide Step 2
        raise NotImplementedError

    def get_active_alerts(self) -> List[Dict]:
        """Get active alerts from Maximo Monitor.

        Returns:
            List of alert dicts with asset_id, severity, message, timestamp
        """
        # TODO: Implement per Build Guide Step 2
        raise NotImplementedError
PYEOF

# ── maximo/workorder_client.py ───────────────────────────────────────────────
mkf "maximo/workorder_client.py" << 'PYEOF'
"""Auto-create work orders in Maximo MAS 9.1.

Called by Build Guide Step 8 (Scheduler) to convert maintenance schedule
into executable work orders in Maximo.

SYNTHETIC DATA DISCLAIMER: All data is computer-generated. Not representative
of any real client operational data.
"""
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MaximoWorkOrderClient:
    """Client for creating work orders in Maximo."""

    def __init__(self, base_url: str, username: str, password: str, site_id: str):
        """
        Args:
            base_url: e.g. https://<your-maximo-host>/maximo
            username: Maximo login
            password: Maximo password
            site_id: Maximo site identifier (e.g. GDCKENYA)
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.site_id = site_id
        self.session: Optional[requests.Session] = None

    def authenticate(self) -> None:
        """Establish authenticated session with Maximo."""
        # TODO: Implement per Build Guide Step 2
        raise NotImplementedError

    def create_work_order(
        self,
        asset_id: str,
        failure_probability: float,
        scheduled_date: str,
        description: str,
    ) -> Dict[str, Any]:
        """Create a preventive maintenance work order.

        Args:
            asset_id: The asset requiring maintenance (e.g. GDC-WP-007)
            failure_probability: Probability of failure if maintenance deferred
            scheduled_date: ISO date string (YYYY-MM-DD) for scheduled maintenance
            description: Work order description text

        Returns:
            Dict with work_order_id (str) and status (str)
        """
        # TODO: Implement per Build Guide Step 2 and Step 8
        raise NotImplementedError

    def get_work_order_status(self, work_order_id: str) -> Dict[str, Any]:
        """Query status of an existing work order.

        Args:
            work_order_id: Maximo work order number

        Returns:
            Dict with status, assigned_tech, completion_date
        """
        # TODO: Implement per Build Guide Step 2
        raise NotImplementedError
PYEOF

# ── ml/__init__.py ────────────────────────────────────────────────────────────
mkf "ml/__init__.py" << 'PYEOF'
"""
Machine Learning Module: LSTM + CNN
Build Guide Steps 4 & 7: Predictive maintenance and visual anomaly detection.

Submodules:
- lstm: Failure prediction (Step 4) — Watson Studio, AUC-ROC > 0.82
- cnn_anomaly: Visual anomaly detection (Step 7) — ResNet-18, >80% accuracy
"""
__version__ = "0.1.0"
PYEOF

mkf "ml/lstm/__init__.py" << 'PYEOF'
"""LSTM Failure Predictor — Build Guide Step 4 (Watson Studio)."""
PYEOF

mkf "ml/cnn_anomaly/__init__.py" << 'PYEOF'
"""CNN Visual Anomaly Detection — Build Guide Step 7 (Watson Studio)."""
PYEOF

# ── ml/lstm/notebooks/01_lstm_training.ipynb ─────────────────────────────────
mkf "ml/lstm/notebooks/01_lstm_training.ipynb" << 'PYEOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# LSTM Failure Predictor — Build Guide Step 4\n",
    "\n",
    "**Dataset:** `datasets/Sensor_Readings.xlsx` (43,800 records, 5 years hourly)\n",
    "\n",
    "**Target:** AUC-ROC > 0.82\n",
    "\n",
    "**Architecture:**\n",
    "- 3 LSTM layers, 64 hidden units each\n",
    "- Dropout 0.2\n",
    "- Sequence length: 720 timesteps (30-day window)\n",
    "- Binary output: failure within next 30 days\n",
    "\n",
    "> ⚠️ SYNTHETIC DATA: All readings are computer-generated. Not representative of any real client operational data.\n",
    "\n",
    "**Run in Watson Studio ML Lab with GPU runtime**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# TODO: Step 4 implementation\n",
    "# 1. Load Sensor_Readings.xlsx from COS bucket\n",
    "# 2. Feature engineering: rolling stats, lag features\n",
    "# 3. Build LSTM model (TensorFlow 2.x)\n",
    "# 4. Train with class weighting (imbalanced failure events)\n",
    "# 5. Evaluate AUC-ROC — target > 0.82\n",
    "# 6. Export model to ml/lstm/models/lstm_v1.h5\n",
    "# 7. Deploy as Watson ML endpoint"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3.10",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.10.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
PYEOF

# ── ml/cnn_anomaly/notebooks/01_cnn_training.ipynb ───────────────────────────
mkf "ml/cnn_anomaly/notebooks/01_cnn_training.ipynb" << 'PYEOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# CNN Anomaly Detector — Build Guide Step 7\n",
    "\n",
    "**Training Data:** Baseline screenshots from Unity 3D model (normal + fault states)\n",
    "\n",
    "**Architecture:** ResNet-18 fine-tuned on ImageNet weights\n",
    "\n",
    "**Target:** >80% accuracy on anomaly classification\n",
    "\n",
    "**Anomaly Types:**\n",
    "- Sensor breach (equipment turns amber/red)\n",
    "- Asset age anomaly (degraded appearance)\n",
    "- Maintenance overdue (blinking indicator)\n",
    "\n",
    "> ⚠️ SYNTHETIC DATA: All data is computer-generated. Not representative of any real client operational data.\n",
    "\n",
    "**Run in Watson Studio ML Lab with GPU runtime**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# TODO: Step 7 implementation\n",
    "# 1. Capture Unity screenshots (normal/amber/red states) → COS bucket\n",
    "# 2. Load and augment image dataset\n",
    "# 3. Fine-tune ResNet-18 (torchvision or tf.keras.applications)\n",
    "# 4. Evaluate — target >80% accuracy\n",
    "# 5. Export to ml/cnn_anomaly/models/cnn_v1.pt\n",
    "# 6. Wrap as REST endpoint for Unity polling"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3.10",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.10.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
PYEOF

# ── scheduler/__init__.py ─────────────────────────────────────────────────────
mkf "scheduler/__init__.py" << 'PYEOF'
"""
Maintenance Scheduler — Build Guide Step 8
Converts Monte Carlo risk outputs into optimized maintenance schedule.

Uses linear programming (scipy.optimize.linprog) to minimise expected cost
subject to:
- Crew availability: max 3 inspections/day
- Equipment interdependencies (compressor → cooler sequencing)
- Regulatory compliance windows (quarterly/annual)
- Monthly budget cap

Output: 90-day Gantt chart + Maximo work orders
"""
__version__ = "0.1.0"
PYEOF

# ── scheduler/optimizer.py ───────────────────────────────────────────────────
mkf "scheduler/optimizer.py" << 'PYEOF'
"""Linear programming optimizer for maintenance schedule.

Build Guide Step 8: Converts Monte Carlo risk outputs into optimal schedule.

Optimization problem:
    min  Σ (maintenance_cost[i] + failure_penalty[i] * P_fail[i] * (1 - x[i]))
    s.t. Σ x[i,t]  ≤ crew_capacity  ∀t      (crew constraint)
         x[i,t]    ∈ {0,1}                   (binary: maintain asset i on day t)
         interdependency constraints
         regulatory window constraints

SYNTHETIC DATA DISCLAIMER: All data is computer-generated. Not representative
of any real client operational data.
"""
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import date, timedelta

logger = logging.getLogger(__name__)


class MaintenanceScheduler:
    """Optimises maintenance schedule using linear programming."""

    CREW_CAPACITY = 3  # max inspections per day

    def __init__(self, crew_capacity: int = CREW_CAPACITY):
        """
        Args:
            crew_capacity: Maximum maintenance tasks per day.
        """
        self.crew_capacity = crew_capacity

    def optimize_schedule(
        self,
        assets: List[Dict[str, Any]],
        failure_probabilities: Dict[str, float],
        horizon_days: int = 90,
        start_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate optimal maintenance schedule.

        Args:
            assets: List of asset dicts — must include:
                    asset_id, replacement_cost_usd, maintenance_cost_usd,
                    last_maintenance_date, maintenance_interval_days
            failure_probabilities: {asset_id: float} from Monte Carlo engine
            horizon_days: Scheduling horizon in days (default 90)
            start_date: Schedule start (defaults to today)

        Returns:
            Dict with keys:
              schedule: [{asset_id, scheduled_date, reason, cost}]
              expected_cost: float
              work_orders: list (for Maximo push)
        """
        # TODO: Implement scipy.optimize.linprog per Build Guide Step 8
        # Phases:
        # 1. Build cost matrix (maintenance cost vs expected failure penalty)
        # 2. Build constraint matrix (crew, interdependencies, regulatory)
        # 3. linprog or PuLP MILP solve
        # 4. Decode solution to schedule list
        raise NotImplementedError

    def generate_gantt(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Gantt chart data structure for visualisation.

        Args:
            schedule: Output of optimize_schedule()

        Returns:
            Dict suitable for Recharts GanttChart or Plotly timeline
        """
        # TODO: Implement Gantt data generation
        raise NotImplementedError
PYEOF

# ── scheduler/constraints.py ─────────────────────────────────────────────────
mkf "scheduler/constraints.py" << 'PYEOF'
"""Constraint definitions for maintenance scheduler.

Build Guide Step 8 constraints:
- Crew availability: 3 inspections/day maximum
- Equipment interdependencies: Compressor must precede cooler maintenance
- Regulatory compliance: Safety relief valve testing quarterly
- Budget limits: Monthly maintenance spend cap
"""
from typing import List, Dict, Any


def get_crew_constraint() -> Dict[str, Any]:
    """Return crew availability constraint."""
    return {
        "type": "max_daily",
        "value": 3,
        "description": "Maximum 3 maintenance inspections per day",
    }


def get_interdependencies() -> List[Dict[str, Any]]:
    """Return equipment interdependency rules."""
    return [
        {
            "parent": "GDC-COMPRESSOR-01",
            "child": "GDC-COOLER-01",
            "type": "must_precede",
            "days_before": 7,
            "reason": "Compressor must run during cooler maintenance window",
        }
    ]


def get_regulatory_windows() -> List[Dict[str, Any]]:
    """Return regulatory compliance requirements."""
    return [
        {
            "asset_class": "PRESSURE_VESSEL",
            "requirement": "quarterly_inspection",
            "max_days_between": 90,
        },
        {
            "asset_class": "SAFETY_VALVE",
            "requirement": "annual_test",
            "max_days_between": 365,
        },
    ]


def get_budget_constraint(monthly_cap_usd: float = 50_000.0) -> Dict[str, Any]:
    """Return monthly budget cap constraint.

    Args:
        monthly_cap_usd: Maximum monthly maintenance spend.
    """
    return {
        "type": "monthly_budget",
        "value": monthly_cap_usd,
        "description": f"Monthly maintenance budget cap: USD {monthly_cap_usd:,.0f}",
    }
PYEOF

# ── scheduler/gantt.py ────────────────────────────────────────────────────────
mkf "scheduler/gantt.py" << 'PYEOF'
"""Generate Gantt chart output for maintenance schedule.

Build Guide Step 8: Visualises 90-day schedule as JSON + PNG.
JSON consumed by React/Recharts; PNG used in reporting PDF.
"""
import json
from typing import Dict, List, Any
from datetime import date


def generate_gantt_json(schedule: Dict[str, Any]) -> str:
    """Serialise schedule as Gantt-compatible JSON.

    Args:
        schedule: Output of MaintenanceScheduler.optimize_schedule()

    Returns:
        JSON string compatible with Recharts timeline component
    """
    # TODO: Implement — map schedule entries to {id, asset_id, start, end, label}
    raise NotImplementedError


def generate_gantt_image(schedule: Dict[str, Any], output_path: str) -> None:
    """Render Gantt chart as PNG.

    Args:
        schedule: Output of MaintenanceScheduler.optimize_schedule()
        output_path: Absolute path for output PNG file
    """
    # TODO: Implement with matplotlib.patches.FancyBboxPatch + timeline
    raise NotImplementedError
PYEOF

# =============================================================================
# [4/6] CREATE OPENSHIFT YAML MANIFESTS
# =============================================================================
step "4/6" "Creating OpenShift / Kustomize manifests"

mkf "deployment/openshift/base/api-deployment.yaml" << 'YAMLEOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ot-twin-api
  namespace: ot-digital-twin
  labels:
    app: ot-twin-api
    part-of: ot-digital-twin
    version: v1.0
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ot-twin-api
  template:
    metadata:
      labels:
        app: ot-twin-api
    spec:
      containers:
      - name: api
        image: ot-twin-api:latest
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: SYNTHETIC_NOTICE
          value: "SYNTHETIC DATA: All readings are computer-generated. Not representative of any real client operational data."
        - name: MAXIMO_BASE_URL
          valueFrom:
            secretKeyRef:
              name: maximo-credentials
              key: url
        - name: MAXIMO_USERNAME
          valueFrom:
            secretKeyRef:
              name: maximo-credentials
              key: username
        - name: MAXIMO_PASSWORD
          valueFrom:
            secretKeyRef:
              name: maximo-credentials
              key: password
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ot-twin-api
  namespace: ot-digital-twin
spec:
  selector:
    app: ot-twin-api
  ports:
  - name: http
    port: 8000
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
YAMLEOF

mkf "deployment/openshift/base/unity-deployment.yaml" << 'YAMLEOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ot-twin-unity
  namespace: ot-digital-twin
  labels:
    app: ot-twin-unity
    part-of: ot-digital-twin
    version: v1.0
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ot-twin-unity
  template:
    metadata:
      labels:
        app: ot-twin-unity
    spec:
      containers:
      - name: unity-webgl
        image: ot-twin-unity:latest
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 80
          protocol: TCP
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ot-twin-unity
  namespace: ot-digital-twin
spec:
  selector:
    app: ot-twin-unity
  ports:
  - name: http
    port: 80
    targetPort: 80
    protocol: TCP
  type: ClusterIP
---
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: ot-twin-unity
  namespace: ot-digital-twin
  annotations:
    haproxy.router.openshift.io/timeout: 60s
spec:
  to:
    kind: Service
    name: ot-twin-unity
  port:
    targetPort: http
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
YAMLEOF

mkf "deployment/openshift/base/kustomization.yaml" << 'YAMLEOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: ot-digital-twin

resources:
- api-deployment.yaml
- unity-deployment.yaml

commonLabels:
  project: ot-digital-twin
  managed-by: kustomize
  team: i3-technologies
YAMLEOF

mkf "deployment/openshift/overlays/dev/kustomization.yaml" << 'YAMLEOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
- ../../base

namePrefix: dev-

patchesStrategicMerge:
- replicas-patch.yaml

commonLabels:
  environment: development
YAMLEOF

mkf "deployment/openshift/overlays/prod/kustomization.yaml" << 'YAMLEOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
- ../../base

commonLabels:
  environment: production
YAMLEOF

# =============================================================================
# [5/6] CREATE STATUS & CONFIG FILES
# =============================================================================
step "5/6" "Creating BUILD_GUIDE_STATUS.md, .env.example, README.md"

mkf "BUILD_GUIDE_STATUS.md" << 'MDEOF'
# OT Digital Twin — Build Guide v1.0 Status Tracker
> **Source of truth:** `docs/Build_Guide_v1.0.pdf`  
> **Last updated:** 28 March 2026  
> **Overall progress:** ▓▓░░░░░░░░░░░░░░ 2/9 steps complete (~22%)

---

## Step Progress

| # | Step | Status | Owner | Evidence Required |
|---|------|--------|-------|-------------------|
| 1 | TechZone Provisioning | ⬜ Not Started | Wisdom | OCP URL, Maximo URL, Watson Studio URL, TechZone reservation IDs |
| 2 | Maximo Monitor Data Load | ⬜ Not Started | Wisdom | Asset hierarchy loaded (50 assets), sensor data points configured, REST API responding |
| 3 | Unity XR 3D Model | ⬜ Not Started | Maurine | `.glb` imported, scene hierarchy matches asset list, colour controller working |
| 4 | LSTM Training (Watson Studio) | ⬜ Not Started | Asenath | AUC-ROC > 0.82, training notebook committed, `.h5` model exported to COS |
| 5 | Monte Carlo with Weibull | ⚠️ Partial | Asenath | Normal → Weibull distributions, sensor covariates integrated, 10k runs < 5s |
| 6 | What-If in Unity | ⬜ Not Started | Maurine | Unity slider UI connected to `/whatif/simulate`, response < 2s, colour update visible |
| 7 | CNN Anomaly AI | ⬜ Not Started | Asenath | >80% accuracy, training notebook committed, Unity polling endpoint live |
| 8 | Maintenance Scheduler | ⬜ Not Started | Asenath | Gantt chart rendered, Maximo WO creation working, LP constraints validated |
| 9 | OpenShift Deployment | ⬜ Not Started | Wisdom | Public OCP Route URL, all pods Running, health checks passing |

---

## Evidence Checklist

### Step 1 — TechZone Provisioning
- [ ] Maximo MAS 9.1 environment reserved and active
- [ ] Watson Studio ML Lab provisioned
- [ ] Red Hat OpenShift 4.14 cluster active
- [ ] All URLs documented in `.env`

### Step 2 — Maximo Monitor Data Load
- [ ] `datasets/GDC_Assets.xlsx` created (50 assets, all columns)
- [ ] `maximo/asset_loader.py` implemented and tested
- [ ] Asset hierarchy visible in Maximo UI
- [ ] `maximo/monitor_client.py` returning live sensor data
- [ ] `/api/assets` endpoint returning Maximo data

### Step 3 — Unity XR 3D Model
- [ ] Well pump `.glb`/`.fbx` CAD model imported
- [ ] `GDCAssetController.cs` attached to all 50 asset GameObjects
- [ ] `ColourController.cs` — green/amber/red state transitions working
- [ ] WebSocket connected to FastAPI stream
- [ ] WebGL build exported to `unity/GDC_Plant_Twin/Builds/WebGL/`

### Step 4 — LSTM Training
- [ ] `datasets/Sensor_Readings.xlsx` exported to Watson Studio COS bucket
- [ ] `ml/lstm/notebooks/01_lstm_training.ipynb` executed successfully
- [ ] AUC-ROC ≥ 0.82 achieved and documented
- [ ] Model deployed as Watson ML REST endpoint
- [ ] `/predict/failure` API endpoint integrated

### Step 5 — Monte Carlo with Weibull
- [ ] Weibull shape (k) and scale (λ) parameters calibrated per asset class
- [ ] Normal distributions replaced in `monte_carlo/engine.py`
- [ ] Sensor covariate modifiers (temperature, vibration → Weibull scale shift)
- [ ] 10,000 runs complete in < 5s (benchmark documented)

### Step 6 — What-If in Unity
- [ ] Unity slider prefabs created for temp/pressure/vibration
- [ ] Slider values POST to `/whatif/simulate`
- [ ] Risk gauge updates in < 2s
- [ ] Probability readout matches API response

### Step 7 — CNN Anomaly AI
- [ ] Unity screenshot dataset captured (min 500 images per class)
- [ ] `ml/cnn_anomaly/notebooks/01_cnn_training.ipynb` executed
- [ ] Accuracy ≥ 80% on test set
- [ ] REST endpoint deployed, Unity polling every 5s

### Step 8 — Maintenance Scheduler
- [ ] `scheduler/optimizer.py` implemented with scipy.optimize or PuLP
- [ ] All constraints validated (crew, interdependencies, regulatory)
- [ ] 90-day Gantt chart rendered in React dashboard
- [ ] Maximo work orders created via `maximo/workorder_client.py`

### Step 9 — OpenShift Deployment
- [ ] Namespace `ot-digital-twin` created
- [ ] All secrets created (`maximo-credentials`, `watson-credentials`)
- [ ] `kustomize build` applies cleanly
- [ ] All pods in Running state
- [ ] Public Route URL accessible and TLS working
- [ ] Health endpoints `/health` and `/ready` returning 200

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| TechZone reservation takes >48h | Medium | High | Reserve immediately; Asenath to escalate via Collins Curtis |
| Unity `.glb` import breaks on WebGL | Medium | High | Test on Three.js viewer first; keep fallback Three.js viewer for demo |
| LSTM AUC-ROC < 0.82 on first run | Medium | Medium | Class weighting, SMOTE oversampling, tune sequence length |
| Maximo REST API schema differs from expected | High | High | Validate with Swagger UI on TechZone instance before coding |
| OpenShift image pull fails (private registry) | Low | High | Push to IBM Cloud Container Registry; configure ImagePullSecret |
| Demo environment cold start latency | Medium | Medium | Warmup script; keep replicas: 2 minimum |

---

## Next Actions (28 March 2026)

1. **Wisdom** — Run this script, commit structure to `dev` branch
2. **Wisdom** — Reserve TechZone: Maximo MAS 9.1 SNO + Watson Studio + OCP
3. **Wisdom** — Generate `datasets/GDC_Assets.xlsx` (50 rows, all columns)
4. **Asenath** — Unblock IBM Cloud credentials via Collins Curtis (TechZone Lab Manager)
5. **Asenath** — Begin Step 5: Weibull parameter research for well pump asset class
6. **Maurine** — Begin Step 3: Import well pump CAD model into Unity, test WebGL export
MDEOF

mkf ".env.example" << 'ENVEOF'
# =============================================================================
# OT Digital Twin — Build Guide v1.0 Environment Variables
# i3 Technologies Ltd / GDC Kenya
# Copy to .env and fill with actual values from TechZone provisioning emails.
# =============================================================================
# ⚠️  NEVER commit .env to Git. .gitignore must include .env
# =============================================================================

# ─── Step 1: TechZone — Maximo MAS 9.1 APM ───────────────────────────────────
MAXIMO_BASE_URL=https://<your-maximo-host>/maximo
MAXIMO_USERNAME=
MAXIMO_PASSWORD=
MAXIMO_SITE_ID=GDCKENYA

# ─── Step 1: TechZone — Watson Studio / watsonx.ai ───────────────────────────
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=https://eu-de.ml.cloud.ibm.com

# ─── Step 1: TechZone — Red Hat OpenShift 4.14 ───────────────────────────────
OPENSHIFT_API_URL=
OPENSHIFT_TOKEN=
OPENSHIFT_CLUSTER_NAME=

# ─── Step 2: Watson IoT Platform ─────────────────────────────────────────────
WATSON_IOT_ORG_ID=
WATSON_IOT_DEVICE_TYPE=geothermal_well_pump
WATSON_IOT_DEVICE_ID=GDC-WP-007
WATSON_IOT_AUTH_TOKEN=
WATSON_IOT_API_KEY=

# ─── Local Development (synthetic data only) ──────────────────────────────────
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_SENSORS=ot-twin-sensors

TIMESCALEDB_URL=postgresql://postgres:password@localhost:5432/otdt
REDIS_URL=redis://localhost:6379

# ─── FastAPI ──────────────────────────────────────────────────────────────────
API_HOST=0.0.0.0
API_PORT=8000
FAILURE_PROBABILITY_ALERT_THRESHOLD=0.25

# ─── System Control ───────────────────────────────────────────────────────────
# SYSTEM_ACTIVE kill switch is controlled by Wisdom Kinoti only.
SYSTEM_ACTIVE=true
DEMO_MODE=false
MAINTENANCE_MSG=System undergoing scheduled maintenance. Back shortly.

# ─── SYNTHETIC DATA DISCLAIMER (MANDATORY — do not remove) ───────────────────
SYNTHETIC_NOTICE="SYNTHETIC DATA: All readings are computer-generated. Not representative of any real client operational data."
ENVEOF

# ── README.md (update if exists, create if not) ───────────────────────────────
cat > "README.md" << 'MDEOF'
# OT Digital Twin — Build Guide v1.0 Implementation

> **Source of truth:** `docs/Build_Guide_v1.0.pdf`  
> **Started:** 28 March 2026  
> **Root:** `Q:\bcs\ibm\EAAAIW @ IBM Research Lab Africa\OTDT\otdt\OTDT`

> ⚠️ **SYNTHETIC DATA:** All sensor readings are computer-generated. Not representative of any real client operational data.

---

## Build Guide Steps

| # | Step | Status | Owner |
|---|------|--------|-------|
| 1 | TechZone Provisioning | ⬜ Not Started | Wisdom |
| 2 | Maximo Monitor Data Load | ⬜ Not Started | Wisdom |
| 3 | Unity XR 3D Model | ⬜ Not Started | Maurine |
| 4 | LSTM Training (Watson Studio) | ⬜ Not Started | Asenath |
| 5 | Monte Carlo with Weibull | ⚠️ Partial | Asenath |
| 6 | What-If in Unity | ⬜ Not Started | Maurine |
| 7 | CNN Anomaly AI | ⬜ Not Started | Asenath |
| 8 | Maintenance Scheduler | ⬜ Not Started | Asenath |
| 9 | OpenShift Deployment | ⬜ Not Started | Wisdom |

Full detail: [BUILD_GUIDE_STATUS.md](BUILD_GUIDE_STATUS.md)

---

## Repository Structure

```
OTDT/
├── api/                    # FastAPI + WebSocket (existing ✅)
├── monte_carlo/            # Monte Carlo engine (existing ✅)
├── sensor_simulator/       # Synthetic data generator (existing ✅)
├── frontend/               # React dashboard (existing ✅, secondary)
├── maximo/                 # Step 2: Maximo MAS 9.1 integration
├── unity/                  # Step 3 & 6: Unity XR 3D model
├── ml/                     # Steps 4 & 7: LSTM + CNN
│   ├── lstm/
│   └── cnn_anomaly/
├── scheduler/              # Step 8: Maintenance optimizer
├── deployment/             # Step 9: OpenShift manifests
│   └── openshift/
│       ├── base/
│       └── overlays/{dev,prod}/
├── datasets/               # GDC_Assets.xlsx, Sensor_Readings.xlsx
├── infrastructure/         # Step 1: TechZone / Terraform
├── scripts/                # Utility scripts (this script)
└── docs/                   # Architecture, API reference
```

---

## Quick Start (local / synthetic data only)

```bash
cp .env.example .env        # fill TechZone credentials
docker-compose up           # starts API + simulator
# React dashboard: http://localhost:3000
# WebSocket:       ws://localhost:8000/twin/stream
# API docs:        http://localhost:8000/docs
```

---

## Team

| Role | Owner | Steps |
|------|-------|-------|
| Infrastructure + API + Deployment | Wisdom Kinoti | 1, 2, 9 |
| Unity XR + Frontend | Maurine Chebet | 3, 6 |
| ML + Monte Carlo + Scheduler | Asenath Atieno Rachael | 4, 5, 7, 8 |

---

## License
i3 Technologies Ltd — Confidential  
IBM & Red Hat Silver Partner | CEID: 7sq30
MDEOF
ok "README.md written"

# =============================================================================
# [6/6] VERIFY & SUMMARY
# =============================================================================
step "6/6" "Verification and summary"

echo ""
echo -e "${BOLD}  Directories created:${NC}"
for d in infrastructure/techzone infrastructure/terraform/ibm_cloud \
          maximo/schemas \
          unity/GDC_Plant_Twin/Assets/Scripts \
          unity/GDC_Plant_Twin/Builds/WebGL \
          unity/ThreeJS_Viewer \
          ml/lstm/notebooks ml/lstm/models ml/lstm/data \
          ml/cnn_anomaly/notebooks ml/cnn_anomaly/models \
          scheduler \
          deployment/openshift/base \
          deployment/openshift/overlays/dev \
          deployment/openshift/overlays/prod \
          deployment/docker \
          datasets docs/architecture docs/api scripts; do
  [ -d "$d" ] && echo -e "    ${GREEN}✔${NC} $d" || echo -e "    ${RED}✖${NC} $d MISSING"
done

echo ""
echo -e "${BOLD}  Key files:${NC}"
for f in maximo/__init__.py maximo/asset_loader.py maximo/monitor_client.py maximo/workorder_client.py \
          ml/__init__.py ml/lstm/__init__.py ml/cnn_anomaly/__init__.py \
          ml/lstm/notebooks/01_lstm_training.ipynb \
          ml/cnn_anomaly/notebooks/01_cnn_training.ipynb \
          scheduler/__init__.py scheduler/optimizer.py scheduler/constraints.py scheduler/gantt.py \
          deployment/openshift/base/api-deployment.yaml \
          deployment/openshift/base/unity-deployment.yaml \
          deployment/openshift/base/kustomization.yaml \
          BUILD_GUIDE_STATUS.md .env.example README.md; do
  [ -f "$f" ] && echo -e "    ${GREEN}✔${NC} $f" || echo -e "    ${RED}✖${NC} $f MISSING"
done

echo ""
echo -e "${BOLD}  Existing code preserved:${NC}"
for d in monte_carlo api sensor_simulator frontend; do
  [ -d "$d" ] && echo -e "    ${GREEN}✔${NC} $d/" || echo -e "    ${YELLOW}⚠${NC}  $d/ not found"
done

echo ""
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  Structure initialized. Build Guide v1.0 — ready to execute.${NC}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BOLD}  Next actions:${NC}"
echo "  1. git add -A && git commit -m 'chore: initialize Build Guide v1.0 structure'"
echo "  2. Reserve TechZone: Maximo MAS 9.1 SNO, Watson Studio, OCP 4.14"
echo "  3. Step 2: implement maximo/asset_loader.py + generate datasets/GDC_Assets.xlsx"
echo "  4. Step 3: Maurine — import well pump CAD into Unity"
echo "  5. Step 5: Asenath — replace Normal with Weibull in monte_carlo/engine.py"
echo ""
echo -e "  Full tracker: ${BLUE}BUILD_GUIDE_STATUS.md${NC}"
echo ""