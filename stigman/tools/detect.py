import subprocess

def detect_os():
    """
    Runs lsb_release -a to detect the OS.
    Returns the distribution description.
    """
    try:
        result = subprocess.run(["lsb_release", "-a"], capture_output=True, text=True, check=True)
        out = result.stdout
        
        # Check if it's Ubuntu 24.04
        if "Ubuntu 24.04" not in out:
            return f"Error: Supported OS is Ubuntu 24.04 LTS. Detected OS info:\n{out}"
        
        # parse out Description
        for line in out.splitlines():
            if line.startswith("Description:"):
                return f"OS Confirmed: {line.split(':', 1)[1].strip()}"
                
        return "Ubuntu 24.04 detected, but couldn't parse Description line."
    except FileNotFoundError:
        return "Error: lsb_release command not found. Are you on Ubuntu?"
    except subprocess.CalledProcessError as e:
        return f"Error running lsb_release: {e.stderr}"
