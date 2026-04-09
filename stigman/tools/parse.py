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
            
        # Optional: build a mapping from Rule ID to Title if present in the document
        rule_titles = {}
        for rule in root.findall('.//xccdf:Rule', ns):
            rule_id = rule.get('id')
            title_elem = rule.find('xccdf:title', ns)
            if rule_id and title_elem is not None:
                rule_titles[rule_id] = title_elem.text
                
        for rule_result in test_result.findall('xccdf:rule-result', ns):
            rule_id_ref = rule_result.get('idref')
            result_elem = rule_result.find('xccdf:result', ns)
            
            if rule_id_ref and result_elem is not None:
                status = result_elem.text
                title = rule_titles.get(rule_id_ref, "Unknown Title")
                
                output.append({
                    "rule_id": rule_id_ref,
                    "title": title,
                    "result": status
                })
                
        return json.dumps(output)
    except Exception as e:
        return f"Error parsing results: {str(e)}"
