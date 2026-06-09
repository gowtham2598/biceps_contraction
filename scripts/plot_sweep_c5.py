import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Define our parameter sweep targets and descriptive placeholders
c5_multipliers = ["0.5", "1.0", "2.0", "4.0"]
labels = {
    "0.5": "0.5x c5 (Degraded/Hypotonic Straightened Fibers)",
    "1.0": "1.0x c5 (Healthy Control Baseline)",
    "2.0": "2.0x c5 (Mild Straightened Fiber Stiffening)",
    "4.0": "4.0x c5 (Severe Straightened Fiber Sclerosis)"
}

repo_root = "."
log_dir = os.path.join(repo_root, "raw_logs/fiber_stiffness_c5")
images_dir = os.path.join(repo_root, "images/fiber_stiffness_c5")

# Safety enforcement: build the specific fiber_stiffness_c5 image vault natively if it doesn't exist
os.makedirs(images_dir, exist_ok=True)

print("="*60)
print("EXTRACTING STREAMS AND REFINING FRAME WINDOW (c5)")
print("="*60)

# 2. Enhanced Core Log Parser Block
def parse_febio_log(filepath):
    times = []
    uz_vals = []
    current_time = 0.0
    
    if not os.path.exists(filepath):
        print(f"Warning: Expected data log path not found: {filepath}")
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

# Pre-load data frames to enable smart dynamic axis scaling
data_vault = {}
for m in c5_multipliers:
    log_filepath = os.path.join(log_dir, f"c5_{m}_disp.txt")
    df = parse_febio_log(log_filepath)
    if not df.empty:
        data_vault[m] = df

# -------------------------------------------------------------
# GRAPH 1: MACRO KINEMATIC TREND
# -------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=150)

for m in c5_multipliers:
    if m in data_vault:
        df = data_vault[m]
        ax1.plot(df['time'], df['uz'], label=labels[m], linewidth=2.5)

ax1.set_xlabel('Simulation Time Frame (s)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Tendon Boundary Z-Displacement, u_z (mm)', fontsize=11, fontweight='bold')
ax1.set_title('Material Sensitivity Analysis: Straightened Fiber Modulus ($c_5$)\nQuantifying Kinematic Effects of Straightened Longitudinal Cable Slopes', fontsize=12, fontweight='bold', pad=12)
ax1.legend(loc='upper left', frameon=True, shadow=False, facecolor='whitesmoke')
ax1.grid(True, linestyle='--', alpha=0.5)

output_image1 = os.path.join(images_dir, 'c5_sweep_comparison.png')
fig1.savefig(output_image1, dpi=150, bbox_inches='tight')
plt.close(fig1)
print(f"[SUCCESS] Global macro-trend graph written to: {output_image1}")

# -------------------------------------------------------------
# GRAPH 2: MICRO-VARIATION REVELATION (REFINED ZOOMED VIEW)
# -------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(10, 6), dpi=150)

terminal_uz_min = float('inf')
terminal_uz_max = float('-inf')

for m in c5_multipliers:
    if m in data_vault:
        df = data_vault[m]
        ax2.plot(df['time'], df['uz'], label=labels[m], linewidth=3)
        
        # Isolate rows in the terminal window to calculate smart boundary bounds
        terminal_df = df[df['time'] >= 29.85]
        if not terminal_df.empty:
            terminal_uz_min = min(terminal_uz_min, terminal_df['uz'].min())
            terminal_uz_max = max(terminal_uz_max, terminal_df['uz'].max())

# Apply dynamic limits based on true data range with a clean 15% padding window
if terminal_uz_min != float('inf') and terminal_uz_max != float('-inf'):
    span = terminal_uz_max - terminal_uz_min
    if span == 0:
        span = 0.001
    ax2.set_xlim(29.85, 30.0)
    ax2.set_ylim(terminal_uz_min - (span * 0.15), terminal_uz_max + (span * 0.15))

ax2.set_xlabel('Simulation Time Frame - Terminal Step Transition (s)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Amplified Tendon Boundary Z-Displacement, u_z (mm)', fontsize=11, fontweight='bold')
ax2.set_title('Straightened Fiber Modulus Sensitivity ($c_5$) [Refined Micro-Scale Window]\nRevealing Latent Divergence via Transverse Radial Bulging Fields', fontsize=12, fontweight='bold', pad=12)
ax2.legend(loc='upper left', frameon=True, shadow=False, facecolor='whitesmoke')
ax2.grid(True, linestyle=':', alpha=0.7)

output_image2 = os.path.join(images_dir, 'c5_sweep_comparison_zoomed.png')
fig2.savefig(output_image2, dpi=150, bbox_inches='tight')
print(f"[SUCCESS] Refined micro-validation graph written to: {output_image2}")
plt.close(fig2)
