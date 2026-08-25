# DHCP-005 — DHCP pool default-router is set to 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/DHCP/DHCP-005/DHCP-005.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: DHCP
- Severity: Medium
- OSI layer: Layer 3 - Network
- Concept: DHCP failures
- Symptom: PCs on VLAN 10 get IP addresses via DHCP (10.10.10.x) and can ping other local hosts, but cannot reach any remote network. Pinging the gateway 10.10.10.1 from the PC fails.
- Topology note: R1 is the DHCP server and gateway (Gi0/0.10 = 10.10.10.1/24) for VLAN 10. 15 PCs in VLAN 10.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: DHCP pool default-router is set to 10.10.10.254 (no device exists at that address) instead of 10.10.10.1 (R1's actual gateway interface). PCs receive the wrong gateway via DHCP and cannot route off-subnet.
- Expected symptom: PCs on VLAN 10 get IP addresses via DHCP (10.10.10.x) and can ping other local hosts, but cannot reach any remote network. Pinging the gateway 10.10.10.1 from the PC fails.
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
 Leased addresses               : 15
 Pending event                  : none

R1# show running-config | section dhcp
ip dhcp excluded-address 10.10.10.1 10.10.10.10
ip dhcp pool VLAN10-POOL
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.254
 dns-server 10.10.10.5

R1# show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0.10      10.10.10.1      YES manual up                    up

C:\> ipconfig
Ethernet adapter Ethernet0:
   IPv4 Address. . . . . . . . . : 10.10.10.11
   Subnet Mask . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . : 10.10.10.254
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
