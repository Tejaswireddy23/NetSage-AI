# GW-004 — The SVI for VLAN 30 has IP address 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/GATEWAY/GW-004/GW-004.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: GATEWAY
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: Default gateway issues
- Symptom: PCs in VLAN 30 (10.10.30.0/24) have IP addresses and the correct gateway 10.10.30.1 configured, but cannot ping the gateway or reach any remote network. PCs in VLAN 10 and 20 work perfectly on the same L3 switch.
- Topology note: MLS1 is a Layer 3 switch (3560) with SVIs for VLANs 10, 20, and 30. VLAN 30 ports are on Fa0/15-Fa0/18. ip routing is enabled.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The SVI for VLAN 30 has IP address 10.10.30.2 but the PCs are configured with default gateway 10.10.30.1. No device owns 10.10.30.1 so the gateway is unreachable.
- Expected symptom: PCs in VLAN 30 (10.10.30.0/24) have IP addresses and the correct gateway 10.10.30.1 configured, but cannot ping the gateway or reach any remote network. PCs in VLAN 10 and 20 work perfectly on the same L3 switch.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
MLS1# show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
Vlan10                     10.10.10.1      YES manual up                    up
Vlan20                     10.10.20.1      YES manual up                    up
Vlan30                     10.10.30.2      YES manual up                    up
FastEthernet0/15           unassigned      YES unset  up                    up
FastEthernet0/16           unassigned      YES unset  up                    up
FastEthernet0/17           unassigned      YES unset  up                    up
FastEthernet0/18           unassigned      YES unset  up                    up

MLS1# show vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
10   Sales                            active    Fa0/1, Fa0/2, Fa0/3
20   HR                               active    Fa0/6, Fa0/7, Fa0/8
30   Engineering                      active    Fa0/15, Fa0/16, Fa0/17, Fa0/18
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
