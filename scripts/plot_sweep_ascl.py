import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Define our physiologically accurate multipliers and descriptive placeholders
ascl_multipliers = ["0.5", "1.0", "1.5", "2.0"]
labels = {
    "0.5": "0.5x ascl (Severe Atrophy / Deep Fatigue State)",
    "1.0": "1.0x ascl (Healthy Control Baseline)",
    "1.5": "1.5x ascl (Hyper-Activation / FES Scenario)",
    "2.0": "2.0x ascl (Acute Inotropic Ceiling / Maximal Voluntary Contraction Boundary)"
}

repo_root = "."
log_dir = os.path.join(repo_root, "raw_logs/active_ascl")
images_dir = os.path.join(repo_root, "images/active_ascl")

# Safety enforcement: ensure the active_ascl image subfolder exists natively
os.makedirs(images_dir, exist_ok=True)

print("="*60)
print("EXTRACTING ACTIVE STREAMS AND GENERATING KINEMATIC GRAPH (ascl)")
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
                    # Store absolute displacement magnitude for cleaner visualization
                    times.append(current_time)
                    uz_vals.append(abs(uz))
                    
    return pd.DataFrame({'time': times, 'uz': uz_vals})

# Load data streams into the workspace memory vault
data_vault = {}
for m in ascl_multipliers:
    log_filepath = os.path.join(log_dir, f"ascl_{m}_disp.txt")
    df = parse_febio_log(log_filepath)
    if not df.empty:
        data_vault[m] = df

# -------------------------------------------------------------
# GRAPH: GLOBAL MACRO KINEMATIC TREND
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

for m in ascl_multipliers:
    if m in data_vault:
        df = data_vault[m]
        ax.plot(df['time'], df['uz'], label=labels[m], linewidth=2.5)

ax.set_xlabel('Simulation Time Frame (s)', fontsize=11, fontweight='bold')
ax.set_ylabel('Tendon Boundary Absolute Z-Displacement, |u_z| (mm)', fontsize=11, fontweight='bold')
ax.set_title('Active Contraction Scale Factor Sensitivity Study ($ascl$)\nQuantifying Global Kinematic Delivery Across Functional Muscle States', fontsize=12, fontweight='bold', pad=12)
ax.legend(loc='upper left', frameon=True, shadow=False, facecolor='whitesmoke')
ax.grid(True, linestyle='--', alpha=0.5)

output_image = os.path.join(images_dir, 'ascl_sweep_comparison.png')
fig.savefig(output_image, dpi=150, bbox_inches='tight')
plt.close(fig)

print(f"[SUCCESS] Global active macro-trend graph successfully written to: {output_image}")
print("="*60)
