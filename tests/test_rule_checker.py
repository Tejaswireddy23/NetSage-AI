"""
tests/test_rule_checker.py
==========================
Pytest tests for checker/rule_checker.py.

Each test uses a hand-written Cisco show-output snippet with a *known,
injected fault* to prove the regex/parsing actually catches it.
"""

import sys
import os

# Ensure the project root is on sys.path so `checker` is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from checker.rule_checker import (  # noqa: E402
    Finding,
    duplicate_ip_check,
    gateway_mismatch_check,
    interface_down_check,
    missing_route_check,
    missing_vlan_check,
    run_all_checks,
    wrong_mask_check,
)


# ── 1. duplicate_ip_check ────────────────────────────────────────────────────


class TestDuplicateIpCheck:
    """Tests for duplicate_ip_check."""

    def test_flags_same_ip_on_two_interfaces(self):
        """Two sub-interfaces share 10.10.10.1 → must flag."""
        output = (
            "R1# show ip interface brief\n"
            "Interface                  IP-Address      OK? Method "
            "Status                Protocol\n"
            "GigabitEthernet0/0.10      10.10.10.1      YES manual "
            "up                    up\n"
            "GigabitEthernet0/0.20      10.10.10.1      YES manual "
            "up                    up\n"
            "GigabitEthernet0/0.30      10.10.30.1      YES manual "
            "up                    up\n"
        )
        findings = duplicate_ip_check(output)
        assert len(findings) >= 1
        f = findings[0]
        assert f.check_name == "duplicate_ip"
        assert f.severity == "Critical"
        assert "10.10.10.1" in f.description
        assert "GigabitEthernet0/0.10" in f.description or \
               "GigabitEthernet0/0.20" in f.description

    def test_clean_when_all_ips_unique(self):
        """Every interface has a distinct IP → no findings."""
        output = (
            "Interface                  IP-Address      OK? Method "
            "Status                Protocol\n"
            "GigabitEthernet0/0.10      10.10.10.1      YES manual "
            "up                    up\n"
            "GigabitEthernet0/0.20      10.10.20.1      YES manual "
            "up                    up\n"
        )
        assert duplicate_ip_check(output) == []

    def test_ignores_same_ip_in_sib_and_arp_for_same_interface(self):
        """The same IP in both SIB and ARP on the same interface is normal."""
        output = (
            "GigabitEthernet0/0.10      10.10.10.1      YES manual "
            "up                    up\n"
            "\n"
            "Internet  10.10.10.1              -   0019.aa6b.3401  "
            "ARPA   GigabitEthernet0/0.10\n"
        )
        assert duplicate_ip_check(output) == []


# ── 2. wrong_mask_check ──────────────────────────────────────────────────────


class TestWrongMaskCheck:
    """Tests for wrong_mask_check."""

    def test_flags_interface_vs_dhcp_pool_mask_mismatch(self):
        """Interface /28, DHCP pool /24 on overlapping subnet → flag."""
        output = (
            "interface GigabitEthernet0/0.20\n"
            " encapsulation dot1Q 20\n"
            " ip address 10.10.20.1 255.255.255.240\n"
            "\n"
            "ip dhcp pool VLAN20\n"
            " network 10.10.20.0 255.255.255.0\n"
            " default-router 10.10.20.1\n"
        )
        findings = wrong_mask_check(output)
        assert len(findings) >= 1
        f = findings[0]
        assert f.check_name == "wrong_mask"
        assert "/28" in f.description or "/24" in f.description

    def test_flags_two_interfaces_overlapping_different_masks(self):
        """Two interfaces on 10.10.10.0 with /24 vs /28 → flag."""
        output = (
            "interface GigabitEthernet0/0.10\n"
            " ip address 10.10.10.1 255.255.255.0\n"
            "interface GigabitEthernet0/0.11\n"
            " ip address 10.10.10.5 255.255.255.240\n"
        )
        findings = wrong_mask_check(output)
        assert len(findings) >= 1
        assert findings[0].check_name == "wrong_mask"

    def test_clean_when_masks_match(self):
        """Same mask on overlapping subnets → no finding."""
        output = (
            "interface GigabitEthernet0/0.10\n"
            " ip address 10.10.10.1 255.255.255.0\n"
            "\n"
            " network 10.10.10.0 255.255.255.0\n"
        )
        assert wrong_mask_check(output) == []


# ── 3. gateway_mismatch_check ────────────────────────────────────────────────


class TestGatewayMismatchCheck:
    """Tests for gateway_mismatch_check."""

    def test_flags_pc_gateway_outside_subnet(self):
        """PC gateway 10.10.20.1 not in 10.10.10.0/24 → flag."""
        output = (
            "C:\\> ipconfig\n"
            "Ethernet adapter Ethernet0:\n"
            "   IPv4 Address. . . . . . . . . : 10.10.10.50\n"
            "   Subnet Mask . . . . . . . . . : 255.255.255.0\n"
            "   Default Gateway . . . . . . . : 10.10.20.1\n"
        )
        findings = gateway_mismatch_check(output)
        assert len(findings) >= 1
        f = findings[0]
        assert f.check_name == "gateway_mismatch"
        assert "10.10.20.1" in f.description
        assert f.severity == "High"

    def test_flags_dhcp_default_router_outside_pool(self):
        """DHCP pool network 10.10.20.0/24, default-router 10.10.10.1 → flag."""
        output = (
            "ip dhcp pool BROKEN-POOL\n"
            " network 10.10.20.0 255.255.255.0\n"
            " default-router 10.10.10.1\n"
            " dns-server 10.10.10.5\n"
        )
        findings = gateway_mismatch_check(output)
        assert len(findings) >= 1
        f = findings[0]
        assert "BROKEN-POOL" in f.description
        assert "10.10.10.1" in f.description

    def test_clean_when_gateway_in_subnet(self):
        """Gateway is inside the host's subnet → no finding."""
        output = (
            "   IPv4 Address. . . . . . . . . : 10.10.10.50\n"
            "   Subnet Mask . . . . . . . . . : 255.255.255.0\n"
            "   Default Gateway . . . . . . . : 10.10.10.1\n"
        )
        assert gateway_mismatch_check(output) == []


# ── 4. interface_down_check ──────────────────────────────────────────────────


class TestInterfaceDownCheck:
    """Tests for interface_down_check."""

    def test_flags_administratively_down(self):
        """An admin-down sub-interface → flag with Medium severity."""
        output = (
            "R1# show ip interface brief\n"
            "Interface                  IP-Address      OK? Method "
            "Status                Protocol\n"
            "GigabitEthernet0/0         unassigned      YES unset  "
            "up                    up\n"
            "GigabitEthernet0/0.10      10.10.10.1      YES manual "
            "administratively down down\n"
            "GigabitEthernet0/0.20      10.10.20.1      YES manual "
            "up                    up\n"
        )
        findings = interface_down_check(output)
        assert len(findings) >= 1
        f = findings[0]
        assert f.check_name == "interface_down"
        assert "GigabitEthernet0/0.10" in f.description
        assert "administratively" in f.description
        assert f.severity == "Medium"

    def test_flags_down_down_as_high(self):
        """A down/down interface (not admin-shutdown) → flag with High."""
        output = (
            "Serial0/0/0                209.165.200.225 YES manual "
            "down                  down\n"
        )
        findings = interface_down_check(output)
        assert len(findings) == 1
        assert findings[0].severity == "High"
        assert "Serial0/0/0" in findings[0].description

    def test_clean_when_all_up(self):
        """All interfaces up/up → no findings."""
        output = (
            "GigabitEthernet0/0.10      10.10.10.1      YES manual "
            "up                    up\n"
            "GigabitEthernet0/0.20      10.10.20.1      YES manual "
            "up                    up\n"
        )
        assert interface_down_check(output) == []


# ── 5. missing_vlan_check ────────────────────────────────────────────────────


class TestMissingVlanCheck:
    """Tests for missing_vlan_check."""

    def test_flags_absent_vlan(self):
        """VLAN 40 expected but missing from switch → flag."""
        output = (
            "SW1# show vlan brief\n"
            "\n"
            "VLAN Name                             Status    Ports\n"
            "---- -------------------------------- --------- ------\n"
            "1    default                          active    Fa0/22\n"
            "10   Sales                            active    Fa0/1\n"
            "20   HR                               active    Fa0/6\n"
            "1002 fddi-default                     act/unsup\n"
        )
        findings = missing_vlan_check(output, expected_vlans=[10, 20, 40])
        assert len(findings) == 1
        f = findings[0]
        assert f.check_name == "missing_vlan"
        assert "40" in f.description
        assert f.severity == "High"

    def test_flags_multiple_missing(self):
        """Two expected VLANs are both absent → two findings."""
        output = (
            "1    default                          active    Fa0/22\n"
            "10   Sales                            active    Fa0/1\n"
        )
        findings = missing_vlan_check(output, expected_vlans=[10, 30, 50])
        assert len(findings) == 2
        missing_ids = {f.description for f in findings}
        assert any("30" in d for d in missing_ids)
        assert any("50" in d for d in missing_ids)

    def test_clean_when_all_present(self):
        """Every expected VLAN is present → no findings."""
        output = (
            "10   Sales                            active    Fa0/1\n"
            "20   HR                               active    Fa0/6\n"
        )
        assert missing_vlan_check(output, expected_vlans=[10, 20]) == []


# ── 6. missing_route_check ───────────────────────────────────────────────────


class TestMissingRouteCheck:
    """Tests for missing_route_check."""

    def test_flags_absent_destination(self):
        """10.10.30.0/24 expected but not in routing table → flag."""
        output = (
            "R1# show ip route\n"
            "Codes: C - connected, S - static\n"
            "\n"
            "Gateway of last resort is not set\n"
            "\n"
            "     10.0.0.0/24 is subnetted, 2 subnets\n"
            "C       10.10.10.0 is directly connected, GigabitEthernet0/0.10\n"
            "C       10.10.20.0 is directly connected, GigabitEthernet0/0.20\n"
        )
        findings = missing_route_check(
            output, expected_destinations=["10.10.30.0/24"]
        )
        assert len(findings) == 1
        f = findings[0]
        assert f.check_name == "missing_route"
        assert "10.10.30.0/24" in f.description

    def test_clean_when_all_routes_covered(self):
        """All expected destinations have matching routes → no findings."""
        output = (
            "     10.0.0.0/24 is subnetted, 3 subnets\n"
            "C       10.10.10.0 is directly connected, GigabitEthernet0/0.10\n"
            "C       10.10.20.0 is directly connected, GigabitEthernet0/0.20\n"
            "S       10.10.30.0 [1/0] via 10.10.99.2\n"
        )
        findings = missing_route_check(
            output,
            expected_destinations=["10.10.10.0/24", "10.10.30.0/24"],
        )
        assert findings == []

    def test_handles_explicit_prefix_in_route(self):
        """Routes with explicit /prefix notation are parsed correctly."""
        output = (
            "     10.0.0.0/8 is variably subnetted, 3 subnets\n"
            "C       10.10.10.0/24 is directly connected, Gi0/0.10\n"
            "C       10.10.99.0/30 is directly connected, Serial0/0/0\n"
            "S       10.10.30.0/24 [1/0] via 10.10.99.2\n"
        )
        # 10.10.30.0/24 IS present — should be clean
        assert (
            missing_route_check(output, expected_destinations=["10.10.30.0/24"])
            == []
        )
        # 192.168.1.0/24 is NOT present — should flag
        findings = missing_route_check(
            output, expected_destinations=["192.168.1.0/24"]
        )
        assert len(findings) == 1


# ── Integration: run_all_checks ──────────────────────────────────────────────


class TestRunAllChecks:
    """Smoke test for the run_all_checks orchestrator."""

    def test_detects_multiple_issues_in_one_case(self):
        """A case with both an admin-down interface and a missing VLAN
        should produce findings from both checks."""
        case = {
            "case_id": "TEST-001",
            "symptom": "No connectivity on VLAN 40",
            "topology_note": "VLAN 40 (Guest) should be on SW1.",
            "show_output": (
                "SW1# show ip interface brief\n"
                "Interface                  IP-Address      OK? Method "
                "Status                Protocol\n"
                "Vlan10                     10.10.10.1      YES manual "
                "up                    up\n"
                "Vlan40                     10.10.40.1      YES manual "
                "administratively down down\n"
                "\n"
                "SW1# show vlan brief\n"
                "\n"
                "VLAN Name                             Status    Ports\n"
                "---- -------------------------------- --------- ------\n"
                "1    default                          active    Fa0/22\n"
                "10   Sales                            active    Fa0/1\n"
                "1002 fddi-default                     act/unsup\n"
            ),
            "expected_fault": "test",
            "osi_layer": "Layer 2",
            "concept_tag": "VLAN misconfiguration",
            "severity": "High",
        }
        findings = run_all_checks(case)
        check_names = {f.check_name for f in findings}
        assert "interface_down" in check_names, (
            "Should flag the admin-down Vlan40 SVI"
        )
        assert "missing_vlan" in check_names, (
            "Should flag VLAN 40 missing from show vlan brief"
        )
