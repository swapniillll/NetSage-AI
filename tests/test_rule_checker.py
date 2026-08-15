import pytest
from scripts.rule_checker import (
    check_duplicate_ip,
    check_wrong_mask,
    check_gateway_mismatch,
    check_interface_down,
    check_missing_vlan,
    check_missing_route,
    run_all,
)

def test_duplicate_ip_positive():
    evidence = "FastEthernet0/0 192.168.10.50 YES\n%IP-4-DUPADDR: Duplicate address 192.168.10.50"
    f = check_duplicate_ip(evidence)
    assert f.rule_name == "check_duplicate_ip"
    assert f.triggered is True
    assert "192.168.10.50" in f.detail

def test_duplicate_ip_negative():
    evidence = "FastEthernet0/0 192.168.10.50 YES"
    f = check_duplicate_ip(evidence)
    assert f.triggered is False

def test_wrong_mask_positive_regression():
    # REGRESSION: Genuine PC-level wrong mask DOES trigger check_wrong_mask
    evidence = """
PC1> ipconfig
IP Address: 192.168.1.10
Subnet Mask: 255.255.255.0
    
PC2> ipconfig
IP Address: 192.168.1.11
Subnet Mask: 255.255.240.0
    """
    f = check_wrong_mask(evidence)
    assert f.rule_name == "check_wrong_mask"
    assert f.triggered is True
    assert "255.255.255.0" in f.detail and "255.255.240.0" in f.detail

def test_wrong_mask_negative_regression():
    # REGRESSION: Legitimate multiple subnet masks on different router interfaces do NOT trigger check_wrong_mask
    evidence = """
R1# show ip interface brief
GigabitEthernet0/0     192.168.1.1     YES manual up                    up
Serial0/0/0            10.0.0.1        YES manual up                    up
R1# show running-config
interface GigabitEthernet0/0
ip address 192.168.1.1 255.255.255.0
interface Serial0/0/0
ip address 10.0.0.1 255.255.255.252
    """
    f = check_wrong_mask(evidence)
    assert f.triggered is False

def test_gateway_mismatch_positive_regression():
    # REGRESSION: A genuine gateway mismatch DOES trigger
    evidence = """
PC1> ipconfig
IP Address: 192.168.1.10
Subnet Mask: 255.255.255.0
Default Gateway: 192.168.1.100
    
R1# show ip interface brief
GigabitEthernet0/0 192.168.1.1 YES manual up up
    """
    f = check_gateway_mismatch(evidence)
    assert f.rule_name == "check_gateway_mismatch"
    assert f.triggered is True
    assert "192.168.1.100" in f.detail

def test_gateway_mismatch_negative_regression():
    # REGRESSION: A server's IP is not incorrectly treated as a router gateway in check_gateway_mismatch
    # Server has .50, PC gateway is .1. If Server is treated as Router, it will trigger false mismatch.
    evidence = """
PC1> ipconfig
IP Address: 192.168.1.10
Subnet Mask: 255.255.255.0
Default Gateway: 192.168.1.1
    
Server1# show ip interface brief
FastEthernet0/0 192.168.1.50 YES manual up up
    """
    f = check_gateway_mismatch(evidence)
    assert f.triggered is False

def test_interface_down_positive():
    evidence = """
R1# show ip interface brief
GigabitEthernet0/0 192.168.1.1 YES manual administratively down down
    """
    f = check_interface_down(evidence)
    assert f.rule_name == "check_interface_down"
    assert f.triggered is True
    assert "GigabitEthernet0/0" in f.detail

def test_interface_down_negative():
    evidence = """
R1# show ip interface brief
GigabitEthernet0/0 192.168.1.1 YES manual up up
    """
    f = check_interface_down(evidence)
    assert f.triggered is False

def test_missing_vlan_positive():
    evidence = """
SW1# show vlan brief
1    default active
10   users active
SW1# show interfaces Fa0/1 switchport
Access VLAN: 30
    """
    f = check_missing_vlan(evidence)
    assert f.rule_name == "check_missing_vlan"
    assert f.triggered is True
    assert "30" in f.detail

def test_missing_vlan_negative():
    evidence = """
SW1# show vlan brief
1    default active
10   users active
SW1# show interfaces Fa0/1 switchport
Access VLAN: 10
    """
    f = check_missing_vlan(evidence)
    assert f.triggered is False

def test_missing_route_positive():
    evidence = """
R1# show ip route
Gateway of last resort is not set
R1# ping 8.8.8.8
    Destination host unreachable
    """
    f = check_missing_route(evidence)
    assert f.rule_name == "check_missing_route"
    assert f.triggered is True

def test_missing_route_negative():
    evidence = """
R1# show ip route
Gateway of last resort is 203.0.113.1 to network 0.0.0.0
R1# ping 8.8.8.8
Reply from 8.8.8.8: bytes=32 time=5ms TTL=128
    """
    f = check_missing_route(evidence)
    assert f.triggered is False

def test_run_all_structure():
    evidence = "some generic evidence"
    findings = run_all(evidence)
    assert len(findings) == 6
    names = {f.rule_name for f in findings}
    assert names == {
        "check_duplicate_ip",
        "check_wrong_mask",
        "check_gateway_mismatch",
        "check_interface_down",
        "check_missing_vlan",
        "check_missing_route"
    }

def test_run_all_no_exceptions_on_valid_inputs():
    evidence = "R1# show ip interface brief\\nGigabitEthernet0/0 192.168.1.1 YES manual up up"
    findings = run_all(evidence)
    for f in findings:
        assert isinstance(f.triggered, bool)
