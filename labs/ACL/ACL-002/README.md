# ACL-002 — ACL 150 is applied outbound on the internal Gi0/0

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ACL/ACL-002/ACL-002.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ACL
- Severity: Critical
- OSI layer: Layer 4 - Transport
- Concept: ACL blocking legitimate traffic
- Symptom: External clients from the internet cannot reach the company's public web server (10.10.30.10 / 203.0.113.10). Internal users can browse the web server fine and can also reach external sites. [RED HERRING: ACL permit statements look correct at first glance.]
- Topology note: R1 has Gi0/0.30 (internal, VLAN 30 with web server) and S0/0/0 (external, 209.165.200.225/30). ACL 150 exists. NAT is configured and working for outbound.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: ACL 150 is applied outbound on the internal Gi0/0.30 interface instead of inbound on the external S0/0/0 interface. Inbound internet traffic on S0/0/0 has no ACL (no filtering), but the permit rules on Gi0/0.30 outbound reference the internal IP which never matches post-NAT traffic flow. The ACL should be applied inbound on S0/0/0 and reference the public IP.
- Expected symptom: External clients from the internet cannot reach the company's public web server (10.10.30.10 / 203.0.113.10). Internal users can browse the web server fine and can also reach external sites. [RED HERRING: ACL permit statements look correct at first glance.]
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show access-lists
Extended IP access list 150
    10 permit tcp any host 10.10.30.10 eq 80 (0 matches)
    20 permit tcp any host 10.10.30.10 eq 443 (0 matches)
    30 permit icmp any any (45 matches)
    40 deny   ip any any (1280 matches)

R1# show ip interface GigabitEthernet0/0.30
GigabitEthernet0/0.30 is up, line protocol is up
  Ingoing access list is not set
  Outgoing access list is 150

R1# show ip interface Serial0/0/0
Serial0/0/0 is up, line protocol is up
  Ingoing access list is not set
  Outgoing access list is not set
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
