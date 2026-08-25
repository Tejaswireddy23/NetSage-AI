# DHCP-003 — The ip helper-address command is missing on MLS1's SVI Vlan40 interface

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/DHCP/DHCP-003/DHCP-003.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: DHCP
- Severity: Medium
- OSI layer: Layer 3 - Network
- Concept: DHCP failures
- Symptom: PCs on VLAN 40 (10.10.40.0/24) receive APIPA addresses. PCs on VLAN 10 on the same switch get DHCP addresses from R1 immediately.
- Topology note: R1 (10.10.10.1) is the DHCP server for all VLANs. MLS1 is an L3 switch with SVIs. VLAN 10 PCs are on the same subnet as R1. VLAN 40 PCs are on a different subnet behind MLS1's SVI Vlan40 (10.10.40.1).

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The ip helper-address command is missing on MLS1's SVI Vlan40 interface. DHCP broadcast DISCOVERs from VLAN 40 clients are not relayed to the DHCP server (R1) on the remote subnet. VLAN 10 works because it is on the same subnet as R1.
- Expected symptom: PCs on VLAN 40 (10.10.40.0/24) receive APIPA addresses. PCs on VLAN 10 on the same switch get DHCP addresses from R1 immediately.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
MLS1# show running-config interface Vlan40
interface Vlan40
 ip address 10.10.40.1 255.255.255.0
 no shutdown

MLS1# show running-config interface Vlan10
interface Vlan10
 ip address 10.10.10.2 255.255.255.0
 ip helper-address 10.10.10.1
 no shutdown

R1# show ip dhcp pool

Pool VLAN40-POOL :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 254
 Leased addresses               : 0
 Pending event                  : none
 1 subnet is currently in the pool :
 Current index        IP address range                    Leased addresses
 10.10.40.1           10.10.40.1       - 10.10.40.254    0
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
