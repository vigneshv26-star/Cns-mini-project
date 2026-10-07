import re

def run_deterministic_checks(show_run_output):
    """
    Mandatory Python string matching/regex checker on raw configuration/show output.
    """
    alerts = []
    # Check for misconfigured subnet mask
    if "255.255.255.255" in show_run_output:
        alerts.append("WARNING: /32 host mask detected on interface.")
    # Check for administratively down interfaces
    if re.search(r'interface(?:(?!interface)[\s\S])*?\bshutdown\b', show_run_output, re.IGNORECASE):
        alerts.append("WARNING: Interface is administratively down.")
    return alerts

def run_rule_checker(show_run_output, expected_gateway=None):
    """
    UI Helper function that returns statuses for visual badges.
    """
    alerts = run_deterministic_checks(show_run_output)
    
    # 1. Interface Check
    intf_match = re.search(r'(?i)interface\s+(\S+)', show_run_output)
    intf_name = intf_match.group(1) if intf_match else "Interface"
    is_shutdown = re.search(r'interface(?:(?!interface)[\s\S])*?\bshutdown\b', show_run_output, re.IGNORECASE) is not None
    interface_status = {
        "status": "FAIL" if is_shutdown else "PASS",
        "label": f"Interface {intf_name} is DOWN" if is_shutdown else f"Interface {intf_name} is UP",
        "badge": f"❌ Interface {intf_name} is DOWN" if is_shutdown else f"✅ Interface {intf_name} is UP"
    }
    
    # 2. Subnet Mask Check
    has_host_mask = "255.255.255.255" in show_run_output
    mask_status = {
        "status": "FAIL" if has_host_mask else "PASS",
        "label": "Host mask (/32) detected" if has_host_mask else "Valid subnet mask",
        "badge": "❌ /32 host mask detected on interface" if has_host_mask else "✅ Subnet mask is valid"
    }
    
    # 3. Gateway Match Check
    gateway_status = {
        "status": "PASS",
        "label": "No gateway checks required",
        "badge": "✅ Gateway checks not applicable"
    }
    
    if expected_gateway and expected_gateway != "None":
        # Extract IP addresses
        ip_matches = re.findall(r'ip address\s+(\d+\.\d+\.\d+\.\d+)', show_run_output, re.IGNORECASE)
        if expected_gateway in ip_matches:
            gateway_status = {
                "status": "PASS",
                "label": "Gateway Match",
                "badge": f"✅ Gateway Match ({expected_gateway})"
            }
        elif ip_matches:
            gateway_status = {
                "status": "FAIL",
                "label": "Gateway Mismatch",
                "badge": f"❌ Gateway Mismatch: Expected {expected_gateway}, found {ip_matches[0]}"
            }
        else:
            gateway_status = {
                "status": "FAIL",
                "label": "Gateway IP Missing",
                "badge": f"❌ Gateway IP missing (expected {expected_gateway})"
            }
            
    return {
        "alerts": alerts,
        "interface": interface_status,
        "mask": mask_status,
        "gateway": gateway_status
    }
