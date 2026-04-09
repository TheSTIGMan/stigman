import json
import xml.etree.ElementTree as ET
import os

def parse_results():
    """
    Parses the XCCDF results XML from /tmp/stigman-results.xml.
    Returns a JSON string of array of {rule_id, title, result}.
    """
    results_file = "/tmp/stigman-results.xml"
    if not os.path.exists(results_file):
        return "Error: Results file not found. Please run a scan first."
        
    try:
        tree = ET.parse(results_file)
        root = tree.getroot()
        
        ns = {'xccdf': 'http://checklists.nist.gov/xccdf/1.2'}
        
        # We need to match Rule-results to the actual Rule titles.
        # But for simplicity, we can extract rule-id from rule-result, 
        # and if we need titles, we'd have to look up the rule definitions.
        # Let's extract rule-results first.
        output = []
        
        test_result = root.find('.//xccdf:TestResult', ns)
        if test_result is None:
            return "Error: No TestResult found in the XML."
            
        pass_count = 0
        fail_count = 0
        total_evaluated = 0
        failed_rules = []

        # Only keep actionable results - skip notselected/notapplicable/notchecked
        SKIP_STATUSES = {"notselected", "notapplicable", "notchecked", "informational"}

        for rule_result in test_result.findall('xccdf:rule-result', ns):
            rule_id_ref = rule_result.get('idref')
            result_elem = rule_result.find('xccdf:result', ns)
            
            if rule_id_ref and result_elem is not None:
                status = result_elem.text
                if status in SKIP_STATUSES:
                    continue
                    
                total_evaluated += 1
                if status == "pass":
                    pass_count += 1
                elif status == "fail":
                    fail_count += 1
                    # Text compression: return only the rule ID for failures
                    failed_rules.append(rule_id_ref)

        # Prepend a brief stats header so the LLM has context without re-counting
        summary = {
            "_summary": {
                "evaluated": total_evaluated,
                "pass": pass_count,
                "fail": fail_count,
            },
            "failed_rules": failed_rules
        }
        return json.dumps(summary)
    except Exception as e:
        return f"Error parsing results: {str(e)}"
