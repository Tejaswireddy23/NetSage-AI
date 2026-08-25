# ACL-001 — ACL 101 line 20 explicitly denies TCP port 80 (HTTP) traffic from VLAN 10 to host 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ACL/ACL-001/ACL-001.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ACL
- Severity: High
- OSI layer: Layer 4 - Transport
- Concept: ACL blocking legitimate traffic
- Symptom: PCs on VLAN 10 can ping the web server at 10.10.30.10 but cannot browse to it (HTTP connection times out). All other servers are reachable on all protocols.
- Topology note: R1 has ACL 101 applied inbound on Gi0/0.10 (VLAN 10 interface). Web server is on VLAN 30 at 10.10.30.10.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: ACL 101 line 20 explicitly denies TCP port 80 (HTTP) traffic from VLAN 10 to host 10.10.30.10. ICMP is permitted on line 10, which is why ping works. The deny rule should be removed or changed to permit.
- Expected symptom: PCs on VLAN 10 can ping the web server at 10.10.30.10 but cannot browse to it (HTTP connection times out). All other servers are reachable on all protocols.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show access-lists
Extended IP access list 101
    10 permit icmp 10.10.10.0 0.0.0.255 any (280 matches)
    20 deny   tcp 10.10.10.0 0.0.0.255 host 10.10.30.10 eq 80 (156 matches)
    30 permit ip any any (4520 matches)

R1# show ip interface GigabitEthernet0/0.10
GigabitEthernet0/0.10 is up, line protocol is up
  Ingoing access list is 101
  Outgoing access list is not set
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
