import subprocess

def check_prerequisites():
    """
    Checks if openscap-scanner and ssg-ubuntu2404 packages are installed via dpkg -l.
    If missing, installs them with sudo apt install -y.
    Returns status of what was found/installed.
    """
    packages = ["libopenscap8", "openscap-scanner"]
    missing = []
    
    report = []
    
    for pkg in packages:
        result = subprocess.run(["dpkg", "-l", pkg], capture_output=True, text=True)
        if result.returncode != 0:
            missing.append(pkg)
        else:
            report.append(f"{pkg} is already installed.")
            
    if missing:
        report.append(f"Missing packages detected: {', '.join(missing)}. Installing...")
        try:
            import os
            env = os.environ.copy()
            env["DEBIAN_FRONTEND"] = "noninteractive"
            
            # Enable universe repo as SSG and OpenSCAP are traditionally stored there
            subprocess.run(["add-apt-repository", "universe", "-y"], capture_output=True, env=env)
            # Fetch latest package lists
            subprocess.run(["apt", "update"], capture_output=True, env=env)
            
            # Note: The tool assumes it is running as root (checked in main) so sudo is just defensive or redundant
            install_cmd = ["apt", "install", "-y"] + missing
            install_res = subprocess.run(install_cmd, capture_output=True, text=True, check=True, env=env)
            report.append(f"Successfully installed: {', '.join(missing)}.")
        except subprocess.CalledProcessError as e:
            return f"Error installing packages. STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
            
    return "\n".join(report)
