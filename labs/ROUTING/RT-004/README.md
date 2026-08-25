# RT-004 — R1's Gi0/0 is in OSPF Area 0 while R2's Gi0/0 is in OSPF Area 1

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ROUTING/RT-004/RT-004.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ROUTING
- Severity: Critical
- OSI layer: Layer 3 - Network
- Concept: Routing
- Symptom: R1 and R2 are running OSPF but the neighbor adjacency never forms. Both interfaces are up/up and can ping each other. [RED HERRING: The network statements both cover the correct interface and wildcard masks look reasonable.]
- Topology note: R1 (Gi0/0 = 10.10.99.1/30) connects to R2 (Gi0/0 = 10.10.99.2/30). Both routers run OSPF process 1.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: R1's Gi0/0 is in OSPF Area 0 while R2's Gi0/0 is in OSPF Area 1. OSPF requires matching area IDs on a shared link to form adjacency. The network statements and wildcard masks are correct — a red herring that suggests the OSPF config looks fine at first glance.
- Expected symptom: R1 and R2 are running OSPF but the neighbor adjacency never forms. Both interfaces are up/up and can ping each other. [RED HERRING: The network statements both cover the correct interface and wildcard masks look reasonable.]
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip ospf neighbor
(no neighbors found)

R1# show ip ospf interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet Address 10.10.99.1/30, Area 0, Attached via Network Statement
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 1
  Transmit Delay is 1 sec, State DR, Priority 1
  Hello 10, Dead 40, Retransmit 5

R2# show ip ospf interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet Address 10.10.99.2/30, Area 1, Attached via Network Statement
  Process ID 1, Router ID 2.2.2.2, Network Type BROADCAST, Cost: 1
  Transmit Delay is 1 sec, State DR, Priority 1
  Hello 10, Dead 40, Retransmit 5

R1# show ip protocols
Routing Protocol is "ospf 1"
  Routing for Networks:
    10.10.99.0 0.0.0.3 area 0

R2# show ip protocols
Routing Protocol is "ospf 1"
  Routing for Networks:
    10.10.99.0 0.0.0.3 area 1
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
