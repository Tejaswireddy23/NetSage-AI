# DHCP-002 — DHCP pool VLAN10-POOL is configured with the wrong network statement — 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/DHCP/DHCP-002/DHCP-002.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: DHCP
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: DHCP failures
- Symptom: PCs on VLAN 10 (10.10.10.0/24) receive IP addresses via DHCP but get addresses in the 10.10.20.x range. They cannot communicate with any other VLAN 10 host or the gateway.
- Topology note: R1 is the DHCP server. VLAN 10 uses 10.10.10.0/24 with gateway 10.10.10.1. DHCP pool name is VLAN10-POOL.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: DHCP pool VLAN10-POOL is configured with the wrong network statement — 10.10.20.0/24 instead of 10.10.10.0/24. Clients receive addresses from the wrong subnet and cannot communicate on their actual VLAN.
- Expected symptom: PCs on VLAN 10 (10.10.10.0/24) receive IP addresses via DHCP but get addresses in the 10.10.20.x range. They cannot communicate with any other VLAN 10 host or the gateway.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip dhcp pool

Pool VLAN10-POOL :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 254
 Leased addresses               : 5
 Pending event                  : none
 1 subnet is currently in the pool :
 Current index        IP address range                    Leased addresses
 10.10.20.6           10.10.20.1       - 10.10.20.254    5

R1# show running-config | section dhcp
ip dhcp pool VLAN10-POOL
 network 10.10.20.0 255.255.255.0
 default-router 10.10.10.1
 dns-server 10.10.10.5
ip dhcp excluded-address 10.10.20.1 10.10.20.5
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
