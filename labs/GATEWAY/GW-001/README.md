# GW-001 — PC1's default gateway is manually set to 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/GATEWAY/GW-001/GW-001.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: GATEWAY
- Severity: Medium
- OSI layer: Layer 3 - Network
- Concept: Default gateway issues
- Symptom: PC1 (10.10.10.50/24) can ping PC2 (10.10.10.51/24) on the same subnet but cannot reach the server at 10.10.30.5 or any remote network. Gateway ping from the PC fails.
- Topology note: R1 Gi0/0.10 is the default gateway for VLAN 10 (10.10.10.0/24) at 10.10.10.1. SW1 connects PCs. PC1 was manually configured.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: PC1's default gateway is manually set to 10.10.10.2 which does not exist; the correct gateway address is 10.10.10.1 (R1's Gi0/0.10 subinterface).
- Expected symptom: PC1 (10.10.10.50/24) can ping PC2 (10.10.10.51/24) on the same subnet but cannot reach the server at 10.10.30.5 or any remote network. Gateway ping from the PC fails.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         unassigned      YES unset  up                    up
GigabitEthernet0/0.10      10.10.10.1      YES manual up                    up
GigabitEthernet0/0.20      10.10.20.1      YES manual up                    up
GigabitEthernet0/0.30      10.10.30.1      YES manual up                    up
Serial0/0/0                209.165.200.225 YES manual up                    up

C:\> ipconfig
Ethernet adapter Ethernet0:
   IPv4 Address. . . . . . . . . : 10.10.10.50
   Subnet Mask . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . : 10.10.10.2
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
