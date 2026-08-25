# RT-002 — Static route to 192

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ROUTING/RT-002/RT-002.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ROUTING
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: Routing
- Symptom: Traffic to the branch office network 192.168.1.0/24 is completely blackholed. Ping from R1 to 192.168.1.1 shows 100% packet loss. The serial link between R1 and R2 is up/up.
- Topology note: R1 (S0/0/0 = 10.10.99.1/30) connects to R2 (S0/0/0 = 10.10.99.2/30). R2 connects to the branch at 192.168.1.0/24 via Gi0/0. Static routes are used.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: Static route to 192.168.1.0/24 on R1 points to next-hop 10.10.99.5, which does not exist on the serial link (the valid peer is 10.10.99.2). The link being up is confirmed but the next-hop is unreachable.
- Expected symptom: Traffic to the branch office network 192.168.1.0/24 is completely blackholed. Ping from R1 to 192.168.1.1 shows 100% packet loss. The serial link between R1 and R2 is up/up.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip route
Codes: C - connected, S - static, R - RIP, O - OSPF

Gateway of last resort is not set

     10.0.0.0/8 is variably subnetted, 3 subnets
C       10.10.10.0/24 is directly connected, GigabitEthernet0/0.10
C       10.10.20.0/24 is directly connected, GigabitEthernet0/0.20
C       10.10.99.0/30 is directly connected, Serial0/0/0
S    192.168.1.0/24 [1/0] via 10.10.99.5

R1# show interfaces Serial0/0/0
Serial0/0/0 is up, line protocol is up
  Hardware is GT96K Serial
  Internet address is 10.10.99.1/30
  MTU 1500 bytes, BW 1544 Kbit/sec, DLY 20000 usec

R1# ping 10.10.99.2
Type escape sequence to abort.
!!!!!
Success rate is 100 percent (5/5)

R1# ping 192.168.1.1
Type escape sequence to abort.
.....
Success rate is 0 percent (0/5)
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
