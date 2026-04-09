import os
import shutil
import datetime

def generate_report():
    """
    Copies the HTML report from /tmp/stigman-report.html to ~/stigman-report-{date}.html.
    """
    src = "/tmp/stigman-report.html"
    if not os.path.exists(src):
        return "Error: Report file not found. Please run a scan first."
        
    # Get current date
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    home_dir = os.path.expanduser("~")
    dest = os.path.join(home_dir, f"stigman-report-{date_str}.html")
    
    # Handle filename collisions
    count = 1
    original_dest = dest
    while os.path.exists(dest):
        dest = f"{original_dest.replace('.html', '')}-{count}.html"
        count += 1
        
    try:
        shutil.copy2(src, dest)
        return f"Report successfully saved to: {dest}"
    except Exception as e:
        return f"Error saving report: {str(e)}"
