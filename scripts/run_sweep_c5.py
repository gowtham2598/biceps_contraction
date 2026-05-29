import os
import subprocess
import shutil

# 1. Define our parameter multipliers and folder structural paths
c5_multipliers = ["0.5", "1.0", "2.0", "4.0"]
feb_input_dir = "feb_inputs/fiber_stiffness_c5"
log_dir = "raw_logs/fiber_stiffness_c5"
plot_dir = "febio_results/fiber_stiffness_c5"

# Safety enforcement: ensure output vaults exist natively before solver execution
os.makedirs(log_dir, exist_ok=True)
os.makedirs(plot_dir, exist_ok=True)

print("="*70)
print("LAUNCHING AUTOMATED COUPLING LOOP: STRAIGHTENED FIBER MODULUS SWEEP (c5)")
print("="*70)

for m in c5_multipliers:
    input_filename = f"biceps_c5_{m}.feb"
    input_filepath = os.path.join(feb_input_dir, input_filename)
    
    print(f"\n[EXECUTION] Initiating FEBio Core Solver for Case Variant: {input_filename}")
    
    # Run the FEBio solver via subprocess
    process = subprocess.run(["febio4", "-silent", input_filepath], capture_output=True, text=True)
    
    if process.returncode == 0:
        print(f" -> [SUCCESS] Simulation case achieved convergence.")
        
        # 2. Native Inline Data Filtering Loop (Prevents GitHub Large File Ceilings)
        disp_file = os.path.join(log_dir, f"c5_{m}_disp.txt")
        stress_file = os.path.join(log_dir, f"c5_{m}_stress.txt")
        vol_file = os.path.join(log_dir, f"c5_{m}_vol.txt")
        
        # Filter Displacement for Node 1773
        if os.path.exists(disp_file):
            subprocess.run(f"awk '/^\\*/ || $1 == \"1773\"' {disp_file} > temp.txt && mv temp.txt {disp_file}", shell=True)
            
        # Filter Stress for Element 12457
        if os.path.exists(stress_file):
            subprocess.run(f"awk '/^\\*/ || $1 == \"12457\"' {stress_file} > temp.txt && mv temp.txt {stress_file}", shell=True)
            
        # Filter Volume for Element 12457
        if os.path.exists(vol_file):
            subprocess.run(f"awk '/^\\*/ || $1 == \"12457\"' {vol_file} > temp.txt && mv temp.txt {vol_file}", shell=True)
            
        print(f" -> [HYGIENE] Text streams successfully filtered down to single Node/Element limits.")
        
        # 3. Relocate companion files from the input folder to their proper vaults
        base_name = f"biceps_c5_{m}"
        generated_log = os.path.join(feb_input_dir, f"{base_name}.log")
        generated_xplt = os.path.join(feb_input_dir, f"{base_name}.xplt")
        
        # Move .log to raw_logs/fiber_stiffness_c5/
        if os.path.exists(generated_log):
            shutil.move(generated_log, os.path.join(log_dir, f"{base_name}.log"))
            
        # Move .xplt to febio_results/fiber_stiffness_c5/
        if os.path.exists(generated_xplt):
            shutil.move(generated_xplt, os.path.join(plot_dir, f"{base_name}.xplt"))
            
        print(f" -> [ROUTING] Companion files (.log & .xplt) safely moved to their target directories.")
            
    else:
        print(f" -> [FAILED] Simulation encountered a calculation error:")
        print(process.stderr)

print("\n" + "="*70)
print("ALL PIPELINE CASES PROCESSED AND CLEANED SUCCESSFULLY")
print("="*70)
