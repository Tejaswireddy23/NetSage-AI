# RT-003 — The 172

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ROUTING/RT-003/RT-003.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ROUTING
- Severity: Medium
- OSI layer: Layer 3 - Network
- Concept: Routing
- Symptom: R1 has OSPF configured and can see R2 as a neighbor, but the 172.16.10.0/24 network behind R2's GigabitEthernet0/1 never appears in R1's routing table.
- Topology note: R1 (Gi0/0 = 10.10.99.1/30) and R2 (Gi0/0 = 10.10.99.2/30) run OSPF Area 0. R2 also connects to 172.16.10.0/24 on Gi0/1.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The 172.16.10.0 network is not included in R2's OSPF network statements (only 10.10.99.0 is advertised). OSPF does not advertise Gi0/1's subnet, so R1 never learns the route.
- Expected symptom: R1 has OSPF configured and can see R2 as a neighbor, but the 172.16.10.0/24 network behind R2's GigabitEthernet0/1 never appears in R1's routing table.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           1   FULL/BDR        00:00:35    10.10.99.2      Gi0/0

R1# show ip route ospf
(no OSPF routes found)

R2# show ip protocols
Routing Protocol is "ospf 1"
  Outgoing update filter list for all interfaces is not set
  Incoming update filter list for all interfaces is not set
  Router ID 2.2.2.2
  Number of areas in this router is 1. 1 normal 0 stub 0 nssa
  Routing for Networks:
    10.10.99.0 0.0.0.3 area 0

R2# show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.10.99.2      YES manual up                    up
GigabitEthernet0/1         172.16.10.1     YES manual up                    up
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
