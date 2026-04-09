import subprocess
import os
import urllib.request
import zipfile
import shutil

def run_scan():
    """
    Runs oscap xccdf eval with the Ubuntu 22.04 STIG profile.
    Saves results to /tmp/stigman-results.xml and /tmp/stigman-report.html.
    """
    content_file = "/usr/share/xml/scap/ssg/content/ssg-ubuntu2204-ds.xml"
    
    # Provide a self-healing fallback since Ubuntu 22.04 apt repositories
    # removed the SCAP Security Guide package to encourage Ubuntu Pro adoption.
    if not os.path.exists(content_file):
        fallback_file = "/tmp/ssg-ubuntu2204-ds.xml"
        if not os.path.exists(fallback_file):
            try:
                url = "https://github.com/ComplianceAsCode/content/releases/download/v0.1.74/scap-security-guide-0.1.74.zip"
                zip_path = "/tmp/ssg_release.zip"
                urllib.request.urlretrieve(url, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extract("scap-security-guide-0.1.74/ssg-ubuntu2204-ds.xml", "/tmp/")
                os.rename("/tmp/scap-security-guide-0.1.74/ssg-ubuntu2204-ds.xml", fallback_file)
                # Cleanup extracted directory
                shutil.rmtree("/tmp/scap-security-guide-0.1.74", ignore_errors=True)
            except Exception as e:
                return f"Error downloading fallback datastream for Ubuntu 22.04: {str(e)}"
        if os.path.exists(fallback_file):
            content_file = fallback_file

    cmd = [
        "oscap", "xccdf", "eval",
        "--profile", "xccdf_org.ssgproject.content_profile_stig",
        "--results", "/tmp/stigman-results.xml",
        "--report", "/tmp/stigman-report.html",
        content_file
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
