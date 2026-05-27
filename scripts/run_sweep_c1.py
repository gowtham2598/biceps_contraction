import os
import shutil
import subprocess

# 1. Parameter scope definitions
c1_multipliers = ["0.5", "1.0", "2.0", "4.0"]

# Because the script lives in scripts/, we look one directory up (../) for repository folders
repo_root = ".."
input_dir = os.path.join(repo_root, "feb_inputs/matrix_stiffness_c1")
log_output_dir = os.path.join(repo_root, "raw_logs/matrix_stiffness_c1")
plot_output_dir = os.path.join(repo_root, "febio_plots/matrix_stiffness_c1")

print("="*60)
print("LAUNCHING AUTOMATED FEBIO SIMULATION SUITE (c1 SWEEP)")
print("="*60)

for m in c1_multipliers:
    base_name = f"biceps_c1_{m}"
    input_file = f"{base_name}.feb"
    print(f"--> Solving model with multiplier {m}x: {input_file}...")
    
    # Execute FEBio directly within the subfolder workspace
    process = subprocess.run(
        ["febio4", input_file],
        cwd=input_dir,
        stdout=subprocess.DEVNULL, # Mutes heavy numeric convergence streams
        stderr=subprocess.PIPE
    )
    
    if process.returncode == 0:
        print(f"    [SUCCESS] Run {m}x converged safely.")
        
        # Define paths to files generated in the input directory
        raw_log = os.path.join(input_dir, f"{base_name}.log")
        raw_xplt = os.path.join(input_dir, f"{base_name}.xplt")
        
        # Target relocation folders
        target_log = os.path.join(log_output_dir, f"{base_name}.log")
        target_xplt = os.path.join(plot_output_dir, f"{base_name}.xplt")
        
        # Automatically move files to keep folders immaculate
        if os.path.exists(raw_log):
            shutil.move(raw_log, target_log)
        if os.path.exists(raw_xplt):
            shutil.move(raw_xplt, target_xplt)
            
        print(f"    [CLEANUP] Moved runtime log and visual database to targets.")
    else:
        print(f"    [ERROR] Run {m}x failed to complete safely.")

print("\n" + "="*60)
print("PIPELINE EXECUTION PASS COMPLETE. REPOSITORY ORGANIZED.")
print("="*60)
