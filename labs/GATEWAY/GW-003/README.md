# GW-003 — R1's Gi0/0

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/GATEWAY/GW-003/GW-003.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: GATEWAY
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: Default gateway issues
- Symptom: PCs with IPs 10.10.20.1 through 10.10.20.14 can ping the gateway and reach remote networks. PCs with IPs above 10.10.20.15 (e.g. 10.10.20.20, .50, .100) can ping each other but cannot ping the gateway 10.10.20.1.
- Topology note: R1 Gi0/0.20 is the VLAN 20 gateway. VLAN 20 uses 10.10.20.0/24. About 30 PCs are in this VLAN.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: R1's Gi0/0.20 subinterface is configured with a /28 subnet mask (255.255.255.240) instead of /24 (255.255.255.0), so only hosts in the 10.10.20.0-10.10.20.15 range are considered local; hosts above .15 are unreachable from the gateway.
- Expected symptom: PCs with IPs 10.10.20.1 through 10.10.20.14 can ping the gateway and reach remote networks. PCs with IPs above 10.10.20.15 (e.g. 10.10.20.20, .50, .100) can ping each other but cannot ping the gateway 10.10.20.1.
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

R1# show running-config interface GigabitEthernet0/0.20
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.10.20.1 255.255.255.240
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
