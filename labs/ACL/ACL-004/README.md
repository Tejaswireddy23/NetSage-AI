# ACL-004 — ACL 140 line 10 explicitly denies all ICMP traffic from VLAN 10 to VLAN 30, blocking ping while allowing TCP (HTTP/SSH) and UDP through subsequent permit rules

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ACL/ACL-004/ACL-004.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ACL
- Severity: Low
- OSI layer: Layer 4 - Transport
- Concept: ACL blocking legitimate traffic
- Symptom: PC1 cannot ping the server at 10.10.30.5 — all pings time out. However PC1 can open an HTTP session to 10.10.30.5 in the browser and SSH to it.
- Topology note: R1 has ACL 140 on Gi0/0.10 inbound. VLAN 10 is 10.10.10.0/24, server VLAN 30 is 10.10.30.0/24.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: ACL 140 line 10 explicitly denies all ICMP traffic from VLAN 10 to VLAN 30, blocking ping while allowing TCP (HTTP/SSH) and UDP through subsequent permit rules.
- Expected symptom: PC1 cannot ping the server at 10.10.30.5 — all pings time out. However PC1 can open an HTTP session to 10.10.30.5 in the browser and SSH to it.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show access-lists
Extended IP access list 140
    10 deny   icmp 10.10.10.0 0.0.0.255 10.10.30.0 0.0.0.255 (87 matches)
    20 permit tcp any any (3400 matches)
    30 permit udp any any (1200 matches)
    40 permit ip any any (560 matches)

R1# show ip interface GigabitEthernet0/0.10
GigabitEthernet0/0.10 is up, line protocol is up
  Ingoing access list is 140
  Outgoing access list is not set
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
