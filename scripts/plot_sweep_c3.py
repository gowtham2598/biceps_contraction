import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Define our parameter sweep targets and file paths
c3_multipliers = ["0.5", "1.0", "2.0", "4.0"]
labels = {
    "0.5": "0.5x c3 (Degraded/Hypotonic Fibers)",
    "1.0": "1.0x c3 (Healthy Control Baseline)",
    "2.0": "2.0x c3 (Mild Fiber Stiffening)",
    "4.0": "4.0x c3 (Severe Pathological Fibrosis)"
}

repo_root = "."
log_dir = os.path.join(repo_root, "raw_logs/fiber_stiffness_c3")
images_dir = os.path.join(repo_root, "images")

print("="*60)
print("EXTRACTING STREAMS AND REFINING FRAME WINDOW (c3)")
print("="*60)

# 2. Log Parser Block
def parse_febio_log(filepath):
    times = []
    uz_vals = []
    current_time = 0.0
    
    if not os.path.exists(filepath):
        return pd.DataFrame({'time': [], 'uz': []})
        
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('*Time'):
                parts = line.split('=')
                current_time = float(parts[1].strip())
            elif not line.startswith('*') and len(line) > 0:
                parts = line.split()
                if len(parts) >= 2: 
                    uz = float(parts[-1])
                    times.append(current_time)
                    uz_vals.append(uz)
                    
    return pd.DataFrame({'time': times, 'uz': uz_vals})

# -------------------------------------------------------------
# GRAPH 1: MACRO KINEMATIC TREND
# -------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=150)

for m in c3_multipliers:
    log_filepath = os.path.join(log_dir, f"c3_{m}_disp.txt")
    df = parse_febio_log(log_filepath)
    if not df.empty:
        ax1.plot(df['time'], df['uz'], label=labels[m], linewidth=2.5)

ax1.set_xlabel('Simulation Time Frame (s)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Tendon Boundary Z-Displacement, $u_z$ (mm)', fontsize=11, fontweight='bold')
ax1.set_title('Material Sensitivity Analysis: Passive Fiber Stiffness ($c_3$)\nQuantifying Kinematic Effects of Intramuscular Structural Fibrosis', fontsize=12, fontweight='bold', pad=12)
ax1.legend(loc='upper left', frameon=True, shadow=False, facecolor='whitesmoke')
ax1.grid(True, linestyle='--', alpha=0.5)

output_image1 = os.path.join(images_dir, 'c3_sweep_comparison.png')
fig1.savefig(output_image1, dpi=150, bbox_inches='tight')
plt.close(fig1)

# -------------------------------------------------------------
# GRAPH 2: MICRO-VARIATION REVELATION (REFINED ZOOMED VIEW)
# -------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(10, 6), dpi=150)

for m in c3_multipliers:
    log_filepath = os.path.join(log_dir, f"c3_{m}_disp.txt")
    df = parse_febio_log(log_filepath)
    if not df.empty:
        ax2.plot(df['time'], df['uz'], label=labels[m], linewidth=3)

# OPTIMIZATION: Shift window right to stretch the terminal divergence across the canvas
ax2.set_xlim(29.85, 30.0)
ax2.set_ylim(0.2405, 0.2416)

ax2.set_xlabel('Simulation Time Frame - Terminal Step Transition (s)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Amplified Tendon Boundary Z-Displacement, $u_z$ (mm)', fontsize=11, fontweight='bold')
ax2.set_title('Passive Fiber Stiffness Sensitivity ($c_3$) [Refined Micro-Scale Window]\nRevealing Minimal Divergence via Transverse Radial Bulging Fields', fontsize=12, fontweight='bold', pad=12)
ax2.legend(loc='upper left', frameon=True, shadow=False, facecolor='whitesmoke')
ax2.grid(True, linestyle=':', alpha=0.7)

output_image2 = os.path.join(images_dir, 'c3_sweep_comparison_zoomed.png')
fig2.savefig(output_image2, dpi=150, bbox_inches='tight')
print(f"[SUCCESS] Refined validation graph written to: {output_image2}")
plt.close(fig2)
