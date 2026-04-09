import subprocess

def run_scan():
    """
    Runs oscap xccdf eval with the Ubuntu 24.04 STIG profile.
    Saves results to /tmp/stigman-results.xml and /tmp/stigman-report.html.
    """
    cmd = [
        "oscap", "xccdf", "eval",
        "--profile", "xccdf_org.ssgproject.content_profile_stig",
        "--results", "/tmp/stigman-results.xml",
        "--report", "/tmp/stigman-report.html",
        "/usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml"
    ]
    
    try:
        # oscap eval returns 2 if some rules fail, which is normal.
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode not in [0, 2]:
            return f"Error running scan (Exit code {result.returncode}). STDERR:\n{result.stderr}"
            
        return "Scan complete. Results saved to /tmp/stigman-results.xml and report to /tmp/stigman-report.html."
    except FileNotFoundError:
        return "Error: oscap command not found. Have prerequisites been checked?"
    except Exception as e:
        return f"Unexpected error running scan: {str(e)}"
