import subprocess
import os

def remediate(rule_ids=None):
    """
    Generates and applies a bash remediation script using oscap.
    Optionally filters to a list of rule_ids.
    """
    results_file = "/tmp/stigman-results.xml"
    if not os.path.exists(results_file):
        return "Error: Results file not found. Please run a scan first."
        
    script_file = "/tmp/stigman-remediation.sh"
    
    cmd = [
        "oscap", "xccdf", "generate", "fix",
        "--fix-type", "bash",
        "--result-id", "",
    ]
    
    if rule_ids and isinstance(rule_ids, list) and len(rule_ids) > 0:
        for rid in rule_ids:
            cmd.extend(["--rule", rid])
            
    cmd.append(results_file)
    
    try:
        # Generate script to file
        with open(script_file, "w") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return f"Error generating remediation script. STDERR:\n{result.stderr}"
                
        # Make script executable
        os.chmod(script_file, 0o700)
        
        # Run remediation script
        apply_res = subprocess.run([script_file], capture_output=True, text=True)
        
        output = apply_res.stdout
        if apply_res.stderr:
            output += f"\nSTDERR:\n{apply_res.stderr}"
            
        return f"Remediation script executed.\nOutput:\n{output}"
        
    except Exception as e:
        return f"Unexpected error during remediation: {str(e)}"
