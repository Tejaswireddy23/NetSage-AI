# ACL-003 — ACL 130 only has permit statements for the 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ACL/ACL-003/ACL-003.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ACL
- Severity: Critical
- OSI layer: Layer 4 - Transport
- Concept: ACL blocking legitimate traffic
- Symptom: PCs in VLAN 20 (10.10.20.0/24) cannot reach any resource — not even their own gateway after the first hop. VLAN 10 PCs work normally. An administrator recently added an ACL.
- Topology note: R1 has subinterfaces for VLANs 10 and 20. ACL 130 was applied to Gi0/0.20.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: ACL 130 only has permit statements for the 10.10.10.0/24 (VLAN 10) source network. There is no permit statement for 10.10.20.0/24 traffic. The implicit deny all at the end of the ACL drops all VLAN 20 traffic. The administrator applied a VLAN 10 ACL to the VLAN 20 interface by mistake.
- Expected symptom: PCs in VLAN 20 (10.10.20.0/24) cannot reach any resource — not even their own gateway after the first hop. VLAN 10 PCs work normally. An administrator recently added an ACL.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show access-lists
Extended IP access list 130
    10 permit tcp 10.10.10.0 0.0.0.255 any eq 80 (340 matches)
    20 permit tcp 10.10.10.0 0.0.0.255 any eq 443 (210 matches)
    30 permit icmp 10.10.10.0 0.0.0.255 any (90 matches)

R1# show ip interface GigabitEthernet0/0.20
GigabitEthernet0/0.20 is up, line protocol is up
  Internet address is 10.10.20.1/24
  Ingoing access list is 130
  Outgoing access list is not set
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
