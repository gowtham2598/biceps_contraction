import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Define our calibrated sensitivity spectrum and descriptive labels
camax_multipliers = ["0.0", "2.175", "4.35", "8.7", "17.4"]
labels = {
    "0.0": "camax = 0.0 (Length-Dependency Disabled Control)",
    "2.175": "camax = 2.175 (Hyper-Sensitized Activation Barrier)",
    "4.35": "camax = 4.35 (Standard Calibrated Reference Benchmark)",
    "8.7": "camax = 8.7 (Moderately Desensitized Activation Barrier)",
    "17.4": "camax = 17.4 (Extremely Desensitized Functional Boundary)"
}

repo_root = "."
log_dir = os.path.join(repo_root, "raw_logs/active_camax")
images_dir = os.path.join(repo_root, "images/active_camax")

# Safety enforcement: build the specific image vault subdirectory if it doesn't exist
os.makedirs(images_dir, exist_ok=True)

print("="*60)
print("EXTRACTING CALCIUM SENSITIVITY STREAMS AND PLOTTING (camax)")
print("="*60)

# 2. Core Log Parser Block
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
                    # Convert to absolute magnitude for clear kinematic evaluation
                    uz_vals.append(abs(uz))
                    
    return pd.DataFrame({'time': times, 'uz': uz_vals})

# Load all five data frames into the tracking memory vault
data_vault = {}
for m in camax_multipliers:
    log_filepath = os.path.join(log_dir, f"camax_{m}_disp.txt")
    df = parse_febio_log(log_filepath)
    if not df.empty:
        data_vault[m] = df

# -------------------------------------------------------------
# GRAPH: GLOBAL KINEMATIC TIMELINE COMPARISON
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

# Plot each case variant with distinct, high-contrast line properties
for m in camax_multipliers:
    if m in data_vault:
        df = data_vault[m]
        ax.plot(df['time'], df['uz'], label=labels[m], linewidth=2.5)

ax.set_xlabel('Simulation Time Frame (s)', fontsize=11, fontweight='bold')
ax.set_ylabel('Tendon Boundary Absolute Z-Displacement, |u_z| (mm)', fontsize=11, fontweight='bold')
ax.set_title('Length-Dependent Calcium Activation Study ($camax$)\nEvaluating Kinematic Influence of Intracellular Sensitivity Thresholds', fontsize=12, fontweight='bold', pad=12)
ax.legend(loc='upper left', frameon=True, shadow=False, facecolor='whitesmoke')
ax.grid(True, linestyle='--', alpha=0.5)

output_image = os.path.join(images_dir, 'camax_sweep_comparison.png')
fig.savefig(output_image, dpi=150, bbox_inches='tight')
plt.close(fig)

print(f"[SUCCESS] Calcium sensitivity macro-trend graph written to: {output_image}")
print("="*60)
