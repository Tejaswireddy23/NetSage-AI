# RT-001 — R1 has a static route to 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ROUTING/RT-001/RT-001.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ROUTING
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: Routing
- Symptom: PCs on VLAN 10 (10.10.10.0/24) can reach VLAN 20 (10.10.20.0/24) but cannot reach the server farm on 10.10.30.0/24. Traceroute from PC stops at R1.
- Topology note: R1 has subinterfaces for VLANs 10, 20, 30. R2 connects the server farm 10.10.30.0/24 via a serial link (10.10.99.0/30) to R1. Static routing is used.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: R1 has a static route to 10.10.30.0/24 via R2, but R2 has no return route to 10.10.10.0/24 or 10.10.20.0/24. Packets reach the server farm but replies are dropped by R2 because it has no route back.
- Expected symptom: PCs on VLAN 10 (10.10.10.0/24) can reach VLAN 20 (10.10.20.0/24) but cannot reach the server farm on 10.10.30.0/24. Traceroute from PC stops at R1.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip route
Codes: C - connected, S - static, R - RIP, O - OSPF

Gateway of last resort is not set

     10.0.0.0/8 is variably subnetted, 4 subnets
C       10.10.10.0/24 is directly connected, GigabitEthernet0/0.10
C       10.10.20.0/24 is directly connected, GigabitEthernet0/0.20
C       10.10.99.0/30 is directly connected, Serial0/0/0
S       10.10.30.0/24 [1/0] via 10.10.99.2

R2# show ip route
Codes: C - connected, S - static, R - RIP, O - OSPF

Gateway of last resort is not set

     10.0.0.0/8 is variably subnetted, 2 subnets
C       10.10.30.0/24 is directly connected, GigabitEthernet0/0
C       10.10.99.0/30 is directly connected, Serial0/0/0
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
