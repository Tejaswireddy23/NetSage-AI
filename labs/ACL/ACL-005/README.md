# ACL-005 — ACL 105 line 10 uses wildcard mask 0

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/ACL/ACL-005/ACL-005.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: ACL
- Severity: High
- OSI layer: Layer 4 - Transport
- Concept: ACL blocking legitimate traffic
- Symptom: Hosts with IPs 10.10.10.128 through 10.10.10.254 are blocked from accessing the file server at 10.10.30.5. Hosts 10.10.10.1 through 10.10.10.127 can access it without issues.
- Topology note: R1 has ACL 105 applied inbound on Gi0/0.10. VLAN 10 uses 10.10.10.0/24 with about 60 hosts.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: ACL 105 line 10 uses wildcard mask 0.0.0.127 which only matches hosts 10.10.10.0 through 10.10.10.127. Hosts in the .128-.254 range do not match line 10, fall through to the deny on line 20, and are blocked. The wildcard mask should be 0.0.0.255 to cover the entire /24.
- Expected symptom: Hosts with IPs 10.10.10.128 through 10.10.10.254 are blocked from accessing the file server at 10.10.30.5. Hosts 10.10.10.1 through 10.10.10.127 can access it without issues.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show access-lists
Extended IP access list 105
    10 permit ip 10.10.10.0 0.0.0.127 host 10.10.30.5 (520 matches)
    20 deny   ip any host 10.10.30.5 (340 matches)
    30 permit ip any any (2800 matches)

R1# show ip interface GigabitEthernet0/0.10
GigabitEthernet0/0.10 is up, line protocol is up
  Ingoing access list is 105
  Outgoing access list is not set
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
