import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Define the fixed material constants from your baseline input deck
ca0 = 4.35
beta = 4.75
l0 = 1.58
refl = 2.04  # This is l_r
tmax = 1.0
ascl = 1.0

camax_multipliers = ["0.0", "2.175", "4.35", "8.7", "17.4"]
labels = {
    "0.0": "camax = 0.0 (LDA Disabled Control)",
    "2.175": "camax = 2.175 (Hyper-Sensitized)",
    "4.35": "camax = 4.35 (Standard Calibrated Reference)",
    "8.7": "camax = 8.7 (Moderately Desensitized)",
    "17.4": "camax = 17.4 (Extremely Desensitized)"
}

repo_root = "."
log_dir = os.path.join(repo_root, "raw_logs/active_camax")
images_dir = os.path.join(repo_root, "images/active_camax")

# 2. Parser to extract real time-history from simulation logs
def calculate_simulated_ta(disp_filepath, camax_val):
    times = []
    ta_timeline = []
    
    if not os.path.exists(disp_filepath):
        print(f"Missing file: {disp_filepath}")
        return [], []
        
    current_time = 0.0
    with open(disp_filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('*Time'):
                parts = line.split('=')
                current_time = float(parts[1].strip())
            elif not line.startswith('*') and len(line) > 0:
                parts = line.split()
                if len(parts) >= 2: 
                    uz = float(parts[-1])
                    
                    # Compute real-time physical fiber length based on actual simulation shortening
                    l_current = refl - abs(uz)
                    
                    # Evaluate the official FEBio documentation formula
                    if camax_val == 0.0:
                        eca50 = 0.0
                        fraction = (ca0**2) / (ca0**2 + eca50**2)
                    else:
                        exponent = beta * (l_current - l0)
                        if exponent <= 0:
                            fraction = 0.0
                        else:
                            eca50 = camax_val / np.sqrt(np.exp(exponent) - 1.0)
                            fraction = (ca0**2) / (ca0**2 + eca50**2)
                    
                    # Calculate real active tension capacity at this specific second
                    ta = ascl * tmax * fraction
                    
                    times.append(current_time)
                    ta_timeline.append(ta)
                    
    return times, ta_timeline

# 3. Process all 5 simulation histories
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

for m in camax_multipliers:
    disp_log = os.path.join(log_dir, f"camax_{m}_disp.txt")
    sim_time, sim_ta = calculate_simulated_ta(disp_log, float(m))
    
    if sim_time:
        ax.plot(sim_time, sim_ta, label=labels[m], linewidth=2.5)

ax.set_xlabel('Simulation Time Frame (s)', fontsize=11, fontweight='bold')
ax.set_ylabel('True Active Fiber Tension, $T^a$ (MPa)', fontsize=11, fontweight='bold')
ax.set_title('Simulated Active Tension ($T^a$) Development Over Time\nDerived Analytically from Real Simulation Kinematics History', fontsize=11, fontweight='bold', pad=12)
ax.legend(loc='lower left', frameon=True, facecolor='whitesmoke')
ax.grid(True, linestyle='--', alpha=0.5)

output_image = os.path.join(images_dir, 'simulation_active_tension_curves.png')
fig.savefig(output_image, dpi=150, bbox_inches='tight')
plt.close(fig)

print(f"[SUCCESS] True simulation active tension plot generated at: {output_image}")
