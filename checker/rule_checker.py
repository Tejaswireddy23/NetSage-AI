#!/usr/bin/env python3
"""
checker/rule_checker.py
=======================
Deterministic rule-based validation for Cisco show-command output.

Complements the AI diagnosis by catching config errors an LLM might miss
or hallucinate about.  No AI/LLM calls — pure regex parsing and subnet math.

Usage
-----
    python checker/rule_checker.py data/cases.csv
"""

import csv
import ipaddress
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

try:
    import pandas as pd

    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False

# ── Finding data class ────────────────────────────────────────────────────────


class Finding(NamedTuple):
    """A single diagnostic finding produced by a rule check."""

    check_name: str  # e.g. "duplicate_ip"
    severity: str  # Low | Medium | High | Critical
    description: str  # human-readable explanation
    evidence_line: str  # raw line(s) that triggered the finding


# ── Shared regex fragments & helpers ──────────────────────────────────────────

_IP = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"

_SEVERITY_ORDER = ["Low", "Medium", "High", "Critical"]


def _ip_in_subnet(ip_str: str, net_str: str, mask_str: str) -> bool:
    """Return True if *ip_str* falls within the subnet *net_str*/*mask_str*."""
    try:
        net = ipaddress.IPv4Network(f"{net_str}/{mask_str}", strict=False)
        return ipaddress.IPv4Address(ip_str) in net
    except (ValueError, ipaddress.AddressValueError):
        return False


# ── 1. duplicate_ip_check ────────────────────────────────────────────────────


def duplicate_ip_check(show_output_text: str) -> List[Finding]:
    """Parse ``show ip interface brief`` / ``show arp`` style output and flag
    any IP address assigned to more than one interface or host.
    """
    findings: List[Finding] = []
    # ip → [(source_label, raw_line), ...]
    ip_map: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    # --- show ip interface brief ------------------------------------------
    sib_re = re.compile(
        r"^(\S+)\s+(" + _IP + r")\s+(?:YES|NO)\s+\S+\s+\S+",
        re.MULTILINE,
    )
    for m in sib_re.finditer(show_output_text):
        ip_map[m.group(2)].append((m.group(1), m.group(0).strip()))

    # --- show arp ---------------------------------------------------------
    arp_re = re.compile(
        r"^Internet\s+(" + _IP + r")\s+\S+\s+(\S+)\s+ARPA\s+(\S+)",
        re.MULTILINE,
    )
    for m in arp_re.finditer(show_output_text):
        ip, iface = m.group(1), m.group(3)
        ip_map[ip].append((f"ARP:{iface}", m.group(0).strip()))

    # --- ipconfig output --------------------------------------------------
    ipconfig_re = re.compile(
        r"IPv4 Address[.\s]*:\s*(" + _IP + r")", re.MULTILINE
    )
    for m in ipconfig_re.finditer(show_output_text):
        ip_map[m.group(1)].append(("PC-host", m.group(0).strip()))

    # Detect duplicates — normalise ARP:Gi0/0 → Gi0/0 before comparing
    for ip, entries in ip_map.items():
        normalised = {src.replace("ARP:", "") for src, _ in entries}
        if len(normalised) > 1:
            labels = sorted({src for src, _ in entries})
            findings.append(
                Finding(
                    "duplicate_ip",
                    "Critical",
                    f"IP {ip} appears on multiple interfaces: "
                    f"{', '.join(labels)}",
                    entries[0][1],
                )
            )

    return findings


# ── 2. wrong_mask_check ──────────────────────────────────────────────────────


def wrong_mask_check(show_output_text: str) -> List[Finding]:
    """Flag subnet masks inconsistent with the declared network — e.g. a
    mismatch between an interface mask and a DHCP-pool mask on the same
    logical subnet.
    """
    findings: List[Finding] = []

    # Gather (context_label, ip_or_net, mask, raw_line)
    subnets: List[Tuple[str, str, str, str]] = []

    # -- 'ip address' from running-config ----------------------------------
    current_iface = "unknown"
    for line in show_output_text.splitlines():
        im = re.match(r"^interface\s+(\S+)", line, re.IGNORECASE)
        if im:
            current_iface = im.group(1)
        am = re.match(r"\s+ip address\s+(" + _IP + r")\s+(" + _IP + r")", line)
        if am:
            subnets.append(
                (
                    f"interface:{current_iface}",
                    am.group(1),
                    am.group(2),
                    line.strip(),
                )
            )

    # -- DHCP pool 'network' statement -------------------------------------
    for m in re.finditer(
        r"^\s+network\s+(" + _IP + r")\s+(" + _IP + r")",
        show_output_text,
        re.MULTILINE,
    ):
        subnets.append(("dhcp-pool", m.group(1), m.group(2), m.group(0).strip()))

    # Compare every pair: flag overlapping subnets with different masks
    for i in range(len(subnets)):
        for j in range(i + 1, len(subnets)):
            ctx1, ip1, m1, l1 = subnets[i]
            ctx2, ip2, m2, l2 = subnets[j]
            try:
                net1 = ipaddress.IPv4Network(f"{ip1}/{m1}", strict=False)
                net2 = ipaddress.IPv4Network(f"{ip2}/{m2}", strict=False)
            except ValueError:
                continue
            if net1.overlaps(net2) and net1.prefixlen != net2.prefixlen:
                findings.append(
                    Finding(
                        "wrong_mask",
                        "High",
                        f"{ctx1} ({ip1}/{m1} = /{net1.prefixlen}) and "
                        f"{ctx2} ({ip2}/{m2} = /{net2.prefixlen}) "
                        f"overlap with different mask lengths",
                        l1,
                    )
                )

    return findings


# ── 3. gateway_mismatch_check ────────────────────────────────────────────────


def gateway_mismatch_check(show_output_text: str) -> List[Finding]:
    """Flag when a device's configured default gateway is not on the same
    subnet as its own IP/mask.
    """
    findings: List[Finding] = []

    # --- Windows ipconfig -------------------------------------------------
    host_ip = host_mask = host_gw = None
    for line in show_output_text.splitlines():
        m = re.search(r"IPv4 Address[.\s]*:\s*(" + _IP + r")", line)
        if m:
            host_ip = m.group(1)
        m = re.search(r"Subnet Mask[.\s]*:\s*(" + _IP + r")", line)
        if m:
            host_mask = m.group(1)
        m = re.search(r"Default Gateway[.\s]*:\s*(" + _IP + r")", line)
        if m:
            host_gw = m.group(1)

    if host_ip and host_mask and host_gw:
        if not _ip_in_subnet(host_gw, host_ip, host_mask):
            findings.append(
                Finding(
                    "gateway_mismatch",
                    "High",
                    f"Host gateway {host_gw} is not in the same subnet as "
                    f"{host_ip}/{host_mask}",
                    f"IPv4: {host_ip}, Mask: {host_mask}, Gateway: {host_gw}",
                )
            )

    # --- DHCP pools: default-router vs network ----------------------------
    pool_name: Optional[str] = None
    pool_net = pool_mask = pool_gw = None

    def _flush_pool() -> None:
        nonlocal pool_net, pool_mask, pool_gw
        if pool_name and pool_net and pool_mask and pool_gw:
            if not _ip_in_subnet(pool_gw, pool_net, pool_mask):
                findings.append(
                    Finding(
                        "gateway_mismatch",
                        "High",
                        f"DHCP pool {pool_name}: default-router {pool_gw} "
                        f"is outside network {pool_net}/{pool_mask}",
                        f"network {pool_net} {pool_mask} / "
                        f"default-router {pool_gw}",
                    )
                )
        pool_net = pool_mask = pool_gw = None

    for line in show_output_text.splitlines():
        pm = re.match(r"ip dhcp pool\s+(\S+)", line)
        if pm:
            _flush_pool()
            pool_name = pm.group(1)
            continue
        nm = re.match(r"\s+network\s+(" + _IP + r")\s+(" + _IP + r")", line)
        if nm:
            pool_net, pool_mask = nm.group(1), nm.group(2)
        gm = re.match(r"\s+default-router\s+(" + _IP + r")", line)
        if gm:
            pool_gw = gm.group(1)
    _flush_pool()  # flush the last pool

    return findings


# ── 4. interface_down_check ──────────────────────────────────────────────────


def interface_down_check(show_output_text: str) -> List[Finding]:
    """Parse ``show ip interface brief`` and flag any interface whose status
    or protocol shows *down* or *administratively down*.
    """
    findings: List[Finding] = []
    pattern = re.compile(
        r"^(\S+)\s+(?:" + _IP + r"|unassigned)\s+(?:YES|NO)\s+\S+\s+"
        r"((?:administratively )?(?:up|down))\s+(up|down)",
        re.MULTILINE,
    )
    for m in pattern.finditer(show_output_text):
        iface = m.group(1)
        status = m.group(2).strip()
        protocol = m.group(3).strip()
        line = m.group(0).strip()

        if "down" in status or "down" in protocol:
            if "administratively" in status:
                sev = "Medium"
                desc = (
                    f"{iface} is administratively down — "
                    f"verify whether shutdown is intentional"
                )
            else:
                sev = "High"
                desc = f"{iface} is {status}/{protocol}"
            findings.append(Finding("interface_down", sev, desc, line))

    return findings


# ── 5. missing_vlan_check ────────────────────────────────────────────────────


def _parse_vlan_brief(text: str) -> Set[int]:
    """Extract VLAN IDs present in ``show vlan brief`` output."""
    vlans: Set[int] = set()
    for m in re.finditer(
        r"^(\d+)\s+\S+\s+(?:active|act/unsup|suspend)", text, re.MULTILINE
    ):
        vlans.add(int(m.group(1)))
    return vlans


def missing_vlan_check(
    show_output_text: str,
    expected_vlans: List[int],
) -> List[Finding]:
    """Cross-check ``show vlan brief`` against a list of VLANs the topology
    expects to exist; flag any that are missing.
    """
    findings: List[Finding] = []
    present = _parse_vlan_brief(show_output_text)

    # Only meaningful if we actually parsed some VLANs
    if not present and not expected_vlans:
        return findings
    if not present:
        # No show vlan brief data at all — can't validate
        return findings

    for vlan_id in expected_vlans:
        if vlan_id not in present:
            findings.append(
                Finding(
                    "missing_vlan",
                    "High",
                    f"VLAN {vlan_id} expected by topology but not found in "
                    f"show vlan brief (present: {sorted(present)})",
                    f"VLAN {vlan_id} not found",
                )
            )

    return findings


# ── 6. missing_route_check ───────────────────────────────────────────────────


def _parse_routes(text: str) -> Set[ipaddress.IPv4Network]:
    """Extract destination networks from ``show ip route`` output."""
    networks: Set[ipaddress.IPv4Network] = set()
    inherited_prefix: Optional[int] = None

    for line in text.splitlines():
        # "10.0.0.0/24 is subnetted" or "… is variably subnetted"
        sub_m = re.search(
            r"(" + _IP + r")/(\d+)\s+is\s+(?:variably\s+)?subnetted", line
        )
        if sub_m:
            inherited_prefix = int(sub_m.group(2))
            continue

        # Route entries: code(s) followed by network [/prefix]
        route_m = re.match(
            r"^\s{0,2}([CSROBDNKI*][A-Za-z* ]{0,5})\s{2,}"
            r"(" + _IP + r")(?:/(\d+))?\s",
            line,
        )
        if route_m:
            net_ip = route_m.group(2)
            explicit = route_m.group(3)
            if explicit:
                pfx = int(explicit)
            elif inherited_prefix is not None:
                pfx = inherited_prefix
            else:
                # Classful fallback
                first = int(net_ip.split(".")[0])
                pfx = 8 if first < 128 else (16 if first < 192 else 24)
            try:
                networks.add(
                    ipaddress.IPv4Network(f"{net_ip}/{pfx}", strict=False)
                )
            except ValueError:
                pass

    return networks


def missing_route_check(
    show_output_text: str,
    expected_destinations: List[str],
) -> List[Finding]:
    """Cross-check ``show ip route`` against destination networks the
    topology says should be reachable; flag any without a matching entry.
    """
    findings: List[Finding] = []
    routes = _parse_routes(show_output_text)

    if not routes:
        return findings  # no routing table in output — can't check

    for dest_str in expected_destinations:
        try:
            dest = ipaddress.IPv4Network(dest_str, strict=False)
        except ValueError:
            continue
        covered = any(dest.subnet_of(r) or r == dest for r in routes)
        if not covered:
            findings.append(
                Finding(
                    "missing_route",
                    "High",
                    f"No route covers expected destination {dest}",
                    f"{dest} not in routing table "
                    f"(known: {sorted(str(r) for r in routes)})",
                )
            )

    return findings


# ── Orchestration ─────────────────────────────────────────────────────────────


def _extract_vlans_from_text(text: str) -> List[int]:
    """Heuristically pull VLAN IDs from free-form text (topology note)."""
    vlans: Set[int] = set()
    for m in re.finditer(r"(?:VLAN|Vlan)\s*(\d+)", text):
        v = int(m.group(1))
        if 1 < v < 1002:  # skip default & FDDI/Token-Ring
            vlans.add(v)
    return sorted(vlans)


def _extract_networks_from_text(text: str) -> List[str]:
    """Heuristically pull CIDR networks from free-form text."""
    nets: Set[str] = set()
    for m in re.finditer(r"(" + _IP + r"/\d{1,2})", text):
        try:
            nets.add(str(ipaddress.IPv4Network(m.group(1), strict=False)))
        except ValueError:
            pass
    return sorted(nets)


def run_all_checks(case: Dict[str, str]) -> List[Finding]:
    """Run all six checks against one row from ``cases.csv`` and return a
    combined findings list.
    """
    show = case.get("show_output", "")
    topo = case.get("topology_note", "")

    findings: List[Finding] = []
    findings.extend(duplicate_ip_check(show))
    findings.extend(wrong_mask_check(show))
    findings.extend(gateway_mismatch_check(show))
    findings.extend(interface_down_check(show))

    expected_vlans = _extract_vlans_from_text(topo)
    findings.extend(missing_vlan_check(show, expected_vlans))

    expected_dests = _extract_networks_from_text(topo)
    findings.extend(missing_route_check(show, expected_dests))

    return findings


# ── CLI entry point ───────────────────────────────────────────────────────────


def _print_summary(rows: List[dict]) -> None:
    """Pretty-print a compact summary table to stdout."""
    if not rows:
        print("  (no findings)")
        return
    cols = list(rows[0].keys())
    widths = {
        c: min(60, max(len(c), *(len(str(r.get(c, ""))) for r in rows)))
        for c in cols
    }
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    print(header)
    print(sep)
    for r in rows:
        vals = []
        for c in cols:
            v = str(r.get(c, ""))
            if len(v) > widths[c]:
                v = v[: widths[c] - 1] + "…"
            vals.append(v.ljust(widths[c]))
        print(" | ".join(vals))


def main(csv_path: str) -> None:
    """CLI: load cases, run all checks, print summary, export results CSV."""
    if _HAS_PANDAS:
        df = pd.read_csv(csv_path)
        cases = df.to_dict(orient="records")
    else:
        with open(csv_path, newline="", encoding="utf-8") as fh:
            cases = list(csv.DictReader(fh))

    all_results: List[dict] = []
    summary_rows: List[dict] = []

    print(f"\n{'=' * 72}")
    print(f"  NetSage Rule Checker — processing {len(cases)} case(s)")
    print(f"{'=' * 72}\n")

    for case in cases:
        cid = case.get("case_id", "?")
        findings = run_all_checks(case)

        for f in findings:
            all_results.append(
                {
                    "case_id": cid,
                    "check_name": f.check_name,
                    "severity": f.severity,
                    "description": f.description,
                    "evidence_line": f.evidence_line[:200],
                }
            )

        if findings:
            checks = ", ".join(sorted({f.check_name for f in findings}))
            max_sev = max(
                findings,
                key=lambda f: _SEVERITY_ORDER.index(f.severity)
                if f.severity in _SEVERITY_ORDER
                else 0,
            )
            summary_rows.append(
                {
                    "case_id": cid,
                    "checks_triggered": checks,
                    "severity": max_sev.severity,
                }
            )
            print(
                f"  {cid:<14} {len(findings)} finding(s)  "
                f"[max: {max_sev.severity:<9}]  checks: {checks}"
            )
        else:
            summary_rows.append(
                {
                    "case_id": cid,
                    "checks_triggered": "(none)",
                    "severity": "-",
                }
            )
            print(f"  {cid:<14} 0 findings   [CLEAN]")

    # ── Summary table ─────────────────────────────────────────────────────
    triggered = [r for r in summary_rows if r["checks_triggered"] != "(none)"]
    clean = len(summary_rows) - len(triggered)
    print(f"\n{'─' * 72}")
    print(f"  Total cases: {len(summary_rows)}  |  "
          f"With findings: {len(triggered)}  |  Clean: {clean}")
    print(f"  Total individual findings: {len(all_results)}")
    print(f"{'─' * 72}\n")

    if summary_rows:
        print("  Summary table:\n")
        _print_summary(summary_rows)
        print()

    # ── Write results CSV ─────────────────────────────────────────────────
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "rule_checker_results.csv")

    if _HAS_PANDAS:
        pd.DataFrame(all_results).to_csv(out_path, index=False)
    else:
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            cols = ["case_id", "check_name", "severity",
                    "description", "evidence_line"]
            writer = csv.DictWriter(fh, fieldnames=cols)
            writer.writeheader()
            writer.writerows(all_results)

    print(f"  Results written to {out_path}\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path/to/cases.csv>")
        sys.exit(1)
    main(sys.argv[1])
