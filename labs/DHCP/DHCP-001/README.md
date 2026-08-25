# DHCP-001 — DHCP pool for VLAN 10 is completely exhausted — all 30 addresses in the /27 scope are leased

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/DHCP/DHCP-001/DHCP-001.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: DHCP
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: DHCP failures
- Symptom: Newly connected PCs on VLAN 10 receive 169.254.x.x APIPA addresses. PCs that were already connected and had DHCP leases still work but cannot renew. The switch port LEDs are green.
- Topology note: R1 is the DHCP server for VLAN 10 (10.10.10.0/24). Pool name VLAN10-POOL. VLAN 10 has 28 active hosts. DHCP pool was configured with a /27 network.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: DHCP pool for VLAN 10 is completely exhausted — all 30 addresses in the /27 scope are leased. New clients receive no offer and fall back to APIPA. The pool should be expanded to a /24 to accommodate all hosts.
- Expected symptom: Newly connected PCs on VLAN 10 receive 169.254.x.x APIPA addresses. PCs that were already connected and had DHCP leases still work but cannot renew. The switch port LEDs are green.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip dhcp pool

Pool VLAN10-POOL :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 30
 Leased addresses               : 30
 Pending event                  : none
 0 subnet is currently in the pool :
 Current index        IP address range                    Leased addresses
 10.10.10.31          10.10.10.1       - 10.10.10.30     30

R1# show ip dhcp binding
IP address       Client-ID/              Lease expiration        Type
                 Hardware address
10.10.10.1       0100.1a2b.3c01          Aug 09 2026 08:00 AM    Automatic
10.10.10.2       0100.1a2b.3c02          Aug 09 2026 08:01 AM    Automatic
...
10.10.10.30      0100.1a2b.3c1e          Aug 09 2026 08:30 AM    Automatic

R1# show ip dhcp server statistics
Memory usage         42352
Address pools        1
Database agents      0
Automatic bindings   30
Manual bindings      0
Expired bindings     0
Malformed messages   0
Message              Received
BOOTREQUEST          0
DHCPDISCOVER         45
DHCPREQUEST          30
DHCPINFORM           0
DHCPRELEASE          0
DHCPDECLINE          0
Message              Sent
BOOTREPLY            0
DHCPOFFER            30
DHCPACK              30
DHCPNAK              15
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
