import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Define our parameter sweep targets and file paths
c1_multipliers = ["0.5", "1.0", "2.0", "4.0"]
labels = {
    "0.5": "0.5x c1 (Degraded/Hypotonic Matrix)",
    "1.0": "1.0x c1 (Healthy Control Baseline)",
    "2.0": "2.0x c1 (Mild Matrix Fibrosis)",
    "4.0": "4.0x c1 (Severe Pathological Fibrosis)"
}

# Look one folder up (../) from the scripts/ directory
repo_root = ".."
log_dir = os.path.join(repo_root, "raw_logs/matrix_stiffness_c1")

print("="*60)
print("EXTRACTING NUMERICAL LOG STREAMS AND GENERATING VISUALIZATIONS")
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
                    # Grab the last column representing local Z-displacement (uz)
                    uz = float(parts[-1])
                    times.append(current_time)
                    uz_vals.append(uz)
                    
    return pd.DataFrame({'time': times, 'uz': uz_vals})

# 3. Generate Professional-Grade Sensitivity Curves Plot
fig, ax = plt.subplots(figsize=(9, 5.5))

for m in c1_multipliers:
    log_filepath = os.path.join(log_dir, f"c1_{m}_disp.txt")
    df = parse_febio_log(log_filepath)
    
    if not df.empty:
        ax.plot(df['time'], df['uz'], label=labels[m], linewidth=2)

ax.set_xlabel('Simulation Time Frame (s)', fontsize=11, fontweight='bold')
ax.set_ylabel('Tendon Boundary Z-Displacement, $u_z$ (mm)', fontsize=11, fontweight='bold')
ax.set_title('Material Sensitivity Analysis: Isotropic Matrix Stiffness ($c_1$)\nQuantifying Kinematic Restriction via Pathological Connective Tissue Fibrosis', fontsize=12, fontweight='bold', pad=12)
ax.legend(loc='upper right', frameon=True, shadow=False, facecolor='whitesmoke')
ax.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
output_image = os.path.join(log_dir, 'c1_sweep_comparison.png')
plt.savefig(output_image, dpi=150)
print(f"\n[PLOT GENERATION COMPLETE] Sensitivity graph safely written to: {output_image}")
