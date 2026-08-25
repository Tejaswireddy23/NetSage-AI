# GW-005 — The 'ip routing' command has not been enabled on the L3 switch (show run confirms 'no ip routing')

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/GATEWAY/GW-005/GW-005.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: GATEWAY
- Severity: Critical
- OSI layer: Layer 3 - Network
- Concept: Default gateway issues
- Symptom: PCs in VLAN 10 can ping their gateway (10.10.10.1) and PCs in VLAN 20 can ping their gateway (10.10.20.1), but no PC in VLAN 10 can reach VLAN 20 and vice versa. Both SVIs are up/up. [RED HERRING: A trunk link shows some pruned VLANs that are unrelated.]
- Topology note: MLS1 is a 3560 L3 switch. SVI VLAN 10 = 10.10.10.1/24, SVI VLAN 20 = 10.10.20.1/24. Trunk Gi0/1 connects to an access switch SW2.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The 'ip routing' command has not been enabled on the L3 switch (show run confirms 'no ip routing'). Without it, the switch cannot route between VLANs even though both SVIs are up. The pruned VLAN 30 on the trunk is a red herring — it is irrelevant to the inter-VLAN routing failure.
- Expected symptom: PCs in VLAN 10 can ping their gateway (10.10.10.1) and PCs in VLAN 20 can ping their gateway (10.10.20.1), but no PC in VLAN 10 can reach VLAN 20 and vice versa. Both SVIs are up/up. [RED HERRING: A trunk link shows some pruned VLANs that are unrelated.]
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
MLS1# show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
Vlan10                     10.10.10.1      YES manual up                    up
Vlan20                     10.10.20.1      YES manual up                    up
GigabitEthernet0/1         unassigned      YES unset  up                    up

MLS1# show ip route
Codes: C - connected, S - static, I - IGRP, R - RIP, M - mobile, B - BGP
       O - OSPF, P - IS-IS, E - EGP
Gateway of last resort is not set

     10.0.0.0/24 is subnetted, 2 subnets
C       10.10.10.0 is directly connected, Vlan10
C       10.10.20.0 is directly connected, Vlan20

MLS1# show interfaces trunk
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1,10,20,30

Port        Vlans allowed and active in management domain
Gi0/1       1,10,20

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       1,10,20

MLS1# show running-config | include ip routing
no ip routing
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
