import os
import datetime
import xml.etree.ElementTree as ET

def generate_report():
    """
    Parses /tmp/stigman-results.xml and generates a Markdown report
    at ~/stigman-report-{date}.md.
    """
    src = "/tmp/stigman-results.xml"
    if not os.path.exists(src):
        return "Error: Results file not found. Please run a scan first."
        
    try:
        tree = ET.parse(src)
        root = tree.getroot()
        
        ns = {'xccdf': 'http://checklists.nist.gov/xccdf/1.2'}
        
        # 1. Map Rule IDs to Severities
        rule_severities = {}
        for rule in root.findall('.//xccdf:Rule', ns):
            rule_id = rule.get('id')
            sev = rule.get('severity', 'unknown')
            if rule_id:
                rule_severities[rule_id] = sev

        # 2. Extract Test Results
        test_result = root.find('.//xccdf:TestResult', ns)
        if test_result is None:
            return "Error: No TestResult found in the XML."
            
        pass_count = 0
        fail_count = 0
        na_count = 0
        other_count = 0
        
        high_fail = 0
        med_fail = 0
        low_fail = 0
        
        failed_rules = []

        for rule_result in test_result.findall('xccdf:rule-result', ns):
            rule_id_ref = rule_result.get('idref')
            result_elem = rule_result.find('xccdf:result', ns)
            
            if rule_id_ref and result_elem is not None:
                status = result_elem.text
                if status == "pass":
                    pass_count += 1
                elif status == "fail":
                    fail_count += 1
                    failed_rules.append(rule_id_ref)
                    sev = rule_severities.get(rule_id_ref, 'unknown')
                    if sev == 'high':
                        high_fail += 1
                    elif sev == 'medium':
                        med_fail += 1
                    elif sev == 'low':
                        low_fail += 1
                elif status == "notapplicable":
                    na_count += 1
                else:
                    other_count += 1

        total_scanned = pass_count + fail_count + na_count + other_count
        evaluated_for_compliance = pass_count + fail_count
        compliance_pct = (pass_count / evaluated_for_compliance * 100) if evaluated_for_compliance > 0 else 0.0

        date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # 3. Build Markdown content
        lines = [
            "# OpenSCAP STIG Scan Results",
            "",
            "**System:** Ubuntu 22.04 LTS  ",
            "**Profile:** DISA STIG (xccdf_org.ssgproject.content_profile_stig)  ",
            "**Scan Tool:** OpenSCAP  ",
            f"**Scan Date:** {date_str}  ",
            "",
            "## Executive Summary",
            "",
            f"- **Total Rules Scanned:** {total_scanned}",
            f"- **Passed:** {pass_count}  ",
            f"- **Failed:** {fail_count}  ",
            f"- **Not Applicable:** {na_count}  ",
            f"- **Overall Compliance:** {compliance_pct:.1f}%  ",
            "",
            "**Key Findings:**  ",
            f"- High Severity Failures: {high_fail}  ",
            f"- Medium Severity Failures: {med_fail}  ",
            f"- Low Severity Failures: {low_fail}  ",
            "",
            "## Failed Rules (Requires Action)",
            ""
        ]
        
        for r in failed_rules:
            # Shorten the ID to make it more readable if desired, or leave full
            lines.append(f"- `{r}`")
            
        md_content = "\\n".join(lines) + "\\n"
        
        # 4. Save file
        home_dir = os.path.expanduser("~")
        dest = os.path.join(home_dir, f"stigman-report-{file_date_str}.md")
        
        # Handle filename collisions
        count = 1
        original_dest = dest
        while os.path.exists(dest):
            dest = f"{original_dest.replace('.md', '')}-{count}.md"
            count += 1
            
        with open(dest, 'w') as f:
            f.write(md_content)
            
        return f"Markdown report successfully generated and saved to: {dest}"

    except Exception as e:
        return f"Error generating markdown report: {str(e)}"
