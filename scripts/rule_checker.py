"""
rule_checker.py — Six deterministic rule checks for Cisco show-output evidence.

Each function takes a single `show_outputs` string (the raw text of one or more
Cisco show commands) and returns a Finding indicating whether that specific
fault pattern was detected.

Design notes (PRD §10, TASK-004 prompt):
  - Simplified regex/string matching — NOT a full Cisco CLI parser.
  - Pure functions: no file I/O, no network calls, no external state.
  - Safely importable and unit-testable in isolation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict


# ---------------------------------------------------------------------------
# Finding data structure
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """Result of a single deterministic rule check."""
    rule_name: str
    triggered: bool
    detail: str

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# 1. check_duplicate_ip
# ---------------------------------------------------------------------------

def check_duplicate_ip(show_outputs: str) -> Finding:
    """Detect duplicate IP addresses across interfaces or devices.

    Triggers on:
      - Cisco syslog  %IP-4-DUPADDR
      - Same IP appearing on two different interfaces in show ip interface brief
    """
    rule = "check_duplicate_ip"

    # Pattern 1: Cisco DUPADDR syslog message
    dup_syslog = re.search(
        r"%IP-4-DUPADDR.*?Duplicate address (\S+)", show_outputs, re.IGNORECASE
    )
    if dup_syslog:
        return Finding(
            rule_name=rule,
            triggered=True,
            detail=f"Duplicate IP detected: {dup_syslog.group(1)} "
                   f"(syslog %IP-4-DUPADDR)",
        )

    # Pattern 2: same IP on multiple interfaces in show ip interface brief
    ip_intf = re.findall(
        r"^(\S+)\s+([\d]+\.[\d]+\.[\d]+\.[\d]+)\s+YES",
        show_outputs,
        re.MULTILINE,
    )
    seen: dict[str, str] = {}
    for intf, ip in ip_intf:
        if ip in ("unassigned",):
            continue
        if ip in seen and seen[ip] != intf:
            return Finding(
                rule_name=rule,
                triggered=True,
                detail=f"IP {ip} appears on both {seen[ip]} and {intf}",
            )
        seen[ip] = intf

    # Pattern 3: same IP on two separate ipconfig blocks
    ipconfig_ips = re.findall(
        r"IP Address[.\s]*:\s*([\d]+\.[\d]+\.[\d]+\.[\d]+)", show_outputs
    )
    ip_iface_ips = re.findall(
        r"^\S+\s+([\d]+\.[\d]+\.[\d]+\.[\d]+)\s+YES",
        show_outputs,
        re.MULTILINE,
    )
    all_ips = ipconfig_ips + ip_iface_ips
    all_ips = [ip for ip in all_ips if ip not in ("0.0.0.0", "unassigned")]
    ip_counts: dict[str, int] = {}
    for ip in all_ips:
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
    for ip, count in ip_counts.items():
        if count > 1:
            return Finding(
                rule_name=rule,
                triggered=True,
                detail=f"IP {ip} appears {count} times across devices/interfaces",
            )

    return Finding(rule_name=rule, triggered=False, detail="No duplicate IPs detected")


# ---------------------------------------------------------------------------
# 2. check_wrong_mask
# ---------------------------------------------------------------------------

def check_wrong_mask(show_outputs: str) -> Finding:
    """Detect mismatched subnet masks between devices on the same logical network.

    Triggers when two or more subnet masks are found in the evidence and they
    differ from each other (e.g. one host has /24 and another has /20).
    """
    rule = "check_wrong_mask"

    # Collect masks from ipconfig-style output
    masks_ipconfig = re.findall(
        r"Subnet Mask[.\s]*:\s*([\d]+\.[\d]+\.[\d]+\.[\d]+)", show_outputs
    )

    # Collect masks from running-config style  "ip address X.X.X.X M.M.M.M"
    masks_config = re.findall(
        r"ip address\s+[\d.]+\s+([\d]+\.[\d]+\.[\d]+\.[\d]+)", show_outputs
    )

    # Collect masks from show ip interface brief /X notation
    cidr_masks = re.findall(
        r"Internet [Aa]ddress (?:is )?[\d.]+/(\d+)", show_outputs
    )

    all_masks = masks_ipconfig + masks_config
    # Normalise CIDR to dotted for comparison is complex; keep them separate
    # but still check for CIDR mismatches among themselves
    if len(cidr_masks) > 1 and len(set(cidr_masks)) > 1:
        return Finding(
            rule_name=rule,
            triggered=True,
            detail=f"Mismatched CIDR prefix lengths found: "
                   f"{', '.join('/' + m for m in cidr_masks)}",
        )

    # Check dotted-decimal masks
    unique_masks = set(all_masks)
    zero_masks = {"0.0.0.0"}
    unique_masks -= zero_masks  # ignore unconfigured hosts
    if len(unique_masks) > 1:
        return Finding(
            rule_name=rule,
            triggered=True,
            detail=f"Mismatched subnet masks detected: {', '.join(sorted(unique_masks))}",
        )

    return Finding(rule_name=rule, triggered=False, detail="No subnet mask mismatch detected")


# ---------------------------------------------------------------------------
# 3. check_gateway_mismatch
# ---------------------------------------------------------------------------

def check_gateway_mismatch(show_outputs: str) -> Finding:
    """Detect when a host's default gateway does not match any router interface IP.

    Compares the Default Gateway in ipconfig output against IPs shown in
    show ip interface brief on router/switch.
    """
    rule = "check_gateway_mismatch"

    # Extract default gateway(s) from ipconfig
    gateways = re.findall(
        r"Default Gateway[.\s]*:\s*([\d]+\.[\d]+\.[\d]+\.[\d]+)", show_outputs
    )

    if not gateways:
        return Finding(
            rule_name=rule, triggered=False,
            detail="No default gateway found in evidence to check"
        )

    # Extract router interface IPs from show ip interface brief
    router_ips = re.findall(
        r"^(\S+)\s+([\d]+\.[\d]+\.[\d]+\.[\d]+)\s+YES\s+\S+\s+up\s+up",
        show_outputs,
        re.MULTILINE,
    )
    router_ip_set = {ip for _, ip in router_ips}

    # Also extract from DHCP default-router config
    dhcp_gw = re.findall(r"default-router\s+([\d.]+)", show_outputs)

    for gw in gateways:
        if gw in ("0.0.0.0", ""):
            continue
        # Gateway should match a router interface IP OR a DHCP configured gateway
        if router_ip_set and gw not in router_ip_set:
            return Finding(
                rule_name=rule,
                triggered=True,
                detail=f"Host default gateway {gw} does not match any "
                       f"router interface IP ({', '.join(sorted(router_ip_set))})",
            )
        # Also check if DHCP default-router disagrees with actual router IP
        if dhcp_gw and router_ip_set:
            for dg in dhcp_gw:
                if dg not in router_ip_set:
                    return Finding(
                        rule_name=rule,
                        triggered=True,
                        detail=f"DHCP default-router {dg} does not match "
                               f"router interface IP ({', '.join(sorted(router_ip_set))})",
                    )

    return Finding(
        rule_name=rule, triggered=False,
        detail="Default gateway matches router interface IP"
    )


# ---------------------------------------------------------------------------
# 4. check_interface_down
# ---------------------------------------------------------------------------

def check_interface_down(show_outputs: str) -> Finding:
    """Detect interfaces that are administratively down or have protocol down.

    Looks at show ip interface brief output for non-up states.
    """
    rule = "check_interface_down"

    # Match show ip interface brief lines where Status or Protocol is not "up"
    # Format: InterfaceName  IP  OK?  Method  Status  Protocol
    lines = re.findall(
        r"^(\S+)\s+[\d.]+\s+YES\s+\S+\s+(\S+)\s+(\S+)",
        show_outputs,
        re.MULTILINE,
    )

    down_interfaces = []
    for intf, status, protocol in lines:
        s = status.lower()
        p = protocol.lower()
        if s != "up" or p != "up":
            state = f"{status}/{protocol}"
            down_interfaces.append(f"{intf} ({state})")

    # Also check for "is down" or "is administratively down" in show interface
    explicit_down = re.findall(
        r"^(\S+) is (?:administratively )?down",
        show_outputs,
        re.MULTILINE,
    )
    for intf in explicit_down:
        entry = f"{intf} (down)"
        if entry not in down_interfaces:
            down_interfaces.append(entry)

    if down_interfaces:
        return Finding(
            rule_name=rule,
            triggered=True,
            detail=f"Interface(s) not up: {'; '.join(down_interfaces)}",
        )

    return Finding(
        rule_name=rule, triggered=False,
        detail="All detected interfaces are up/up"
    )


# ---------------------------------------------------------------------------
# 5. check_missing_vlan
# ---------------------------------------------------------------------------

def check_missing_vlan(show_outputs: str) -> Finding:
    """Detect when a port is assigned to a VLAN that does not appear in show vlan brief.

    Also detects when a trunk does not carry an expected VLAN.
    """
    rule = "check_missing_vlan"

    # Extract VLANs that exist from show vlan brief
    # Format: "10   name   active    ports..."
    existing_vlans: set[str] = set()
    for m in re.finditer(
        r"^(\d+)\s+\S+\s+active",
        show_outputs,
        re.MULTILINE,
    ):
        existing_vlans.add(m.group(1))

    # Check Access VLAN from show interfaces switchport
    access_vlan_match = re.search(
        r"Access VLAN:\s*(\d+)", show_outputs
    )
    if access_vlan_match and existing_vlans:
        av = access_vlan_match.group(1)
        if av not in existing_vlans:
            return Finding(
                rule_name=rule,
                triggered=True,
                detail=f"Port is assigned to VLAN {av} but VLAN {av} "
                       f"does not exist on the switch "
                       f"(existing: {', '.join(sorted(existing_vlans, key=int))})",
            )

    # Check trunk allowed VLANs — if a VLAN is expected but not in allowed list
    trunk_allowed = re.search(
        r"Vlans allowed on trunk\s*\n\S+\s+([\d,\-]+)", show_outputs
    )
    if trunk_allowed:
        allowed_str = trunk_allowed.group(1).strip()
        # Expand ranges like "1,20" or "1-5,10"
        allowed_vlans: set[str] = set()
        for part in allowed_str.split(","):
            part = part.strip()
            if "-" in part:
                lo, hi = part.split("-", 1)
                for v in range(int(lo), int(hi) + 1):
                    allowed_vlans.add(str(v))
            else:
                allowed_vlans.add(part)

        # Check if any VLAN that exists on the switch is excluded from the trunk
        if existing_vlans:
            missing_on_trunk = existing_vlans - allowed_vlans - {"1"}  # VLAN 1 special
            if missing_on_trunk:
                return Finding(
                    rule_name=rule,
                    triggered=True,
                    detail=f"VLAN(s) {', '.join(sorted(missing_on_trunk, key=int))} "
                           f"exist on the switch but are not allowed on the trunk "
                           f"(allowed: {allowed_str})",
                )

    return Finding(
        rule_name=rule, triggered=False,
        detail="No missing VLAN issues detected"
    )


# ---------------------------------------------------------------------------
# 6. check_missing_route
# ---------------------------------------------------------------------------

def check_missing_route(show_outputs: str) -> Finding:
    """Detect when the routing table has no route to a destination or has no
    default route when one appears needed.

    Triggers on:
      - "Gateway of last resort is not set" (missing default route)
      - "Destination host unreachable" for a specific ping target that has
        no matching route entry
    """
    rule = "check_missing_route"

    # Pattern 1: explicit "gateway of last resort is not set"
    no_default = re.search(
        r"[Gg]ateway of last resort is not set", show_outputs
    )

    # Pattern 2: "Destination host unreachable" from a failed ping
    unreachable = re.search(
        r"[Dd]estination host unreachable|[Uu]nreachable", show_outputs
    )

    if no_default and unreachable:
        return Finding(
            rule_name=rule,
            triggered=True,
            detail="Gateway of last resort is not set and a destination "
                   "is unreachable — likely missing route or default route",
        )

    if no_default:
        # Only flag if there's evidence of external traffic need
        # (ping to non-connected network, or the word "external" / "internet")
        external_hint = re.search(
            r"ping\s+(?:8\.8\.8\.8|(?:\d+\.){3}\d+).*(?:unreachable|timed out)",
            show_outputs,
            re.IGNORECASE,
        )
        if external_hint:
            return Finding(
                rule_name=rule,
                triggered=True,
                detail="Gateway of last resort is not set; ping to external "
                       "destination failed — missing default route",
            )

    # Pattern 3: static route pointing to unreachable next-hop
    static_routes = re.findall(
        r"S\s+([\d./]+)\s+\[[\d/]+\]\s+via\s+([\d.]+)", show_outputs
    )
    for dest, nexthop in static_routes:
        # Check if a ping to that next-hop failed
        nexthop_fail = re.search(
            rf"ping\s+{re.escape(nexthop)}.*?(?:unreachable|timed out|100 percent loss)",
            show_outputs,
            re.IGNORECASE | re.DOTALL,
        )
        if nexthop_fail:
            return Finding(
                rule_name=rule,
                triggered=True,
                detail=f"Static route to {dest} via {nexthop} but "
                       f"next-hop {nexthop} is unreachable",
            )

    return Finding(
        rule_name=rule, triggered=False,
        detail="No missing route issues detected"
    )


# ---------------------------------------------------------------------------
# run_all — aggregate all six checks
# ---------------------------------------------------------------------------

def run_all(show_outputs: str) -> list[Finding]:
    """Run all 6 deterministic rule checks and return exactly 6 Findings."""
    return [
        check_duplicate_ip(show_outputs),
        check_wrong_mask(show_outputs),
        check_gateway_mismatch(show_outputs),
        check_interface_down(show_outputs),
        check_missing_vlan(show_outputs),
        check_missing_route(show_outputs),
    ]
