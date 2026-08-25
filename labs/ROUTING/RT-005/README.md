# RT-005 — The static route to 172

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ROUTING/RT-005/RT-005.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ROUTING
- Severity: Medium
- OSI layer: Layer 3 - Network
- Concept: Routing
- Symptom: PCs on VLAN 10 can reach the 172.16.0.0/16 data centre network but latency is 150ms+ and traceroute shows 4 extra hops through the WAN. The direct LAN path should be 1 hop.
- Topology note: R1 has two paths to the data centre: a GigabitEthernet link (Gi0/1 = 10.10.50.1/30 to R3 Gi0/0 = 10.10.50.2/30) and a slow serial WAN (S0/0/0 = 10.10.99.1/30 to R2). R2 eventually reaches R3 through R4 and R5.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The static route to 172.16.0.0/16 directs traffic via 10.10.99.2 (the slow Serial WAN link to R2) instead of 10.10.50.2 (the direct GigabitEthernet link to R3). Traffic takes an unnecessary multi-hop WAN path.
- Expected symptom: PCs on VLAN 10 can reach the 172.16.0.0/16 data centre network but latency is 150ms+ and traceroute shows 4 extra hops through the WAN. The direct LAN path should be 1 hop.
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
C       10.10.50.0/30 is directly connected, GigabitEthernet0/1
C       10.10.99.0/30 is directly connected, Serial0/0/0
S    172.16.0.0/16 [1/0] via 10.10.99.2

R1# show interfaces GigabitEthernet0/1
GigabitEthernet0/1 is up, line protocol is up
  Internet address is 10.10.50.1/30
  MTU 1500 bytes, BW 1000000 Kbit/sec

R1# show interfaces Serial0/0/0
Serial0/0/0 is up, line protocol is up
  Internet address is 10.10.99.1/30
  MTU 1500 bytes, BW 1544 Kbit/sec
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
