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
