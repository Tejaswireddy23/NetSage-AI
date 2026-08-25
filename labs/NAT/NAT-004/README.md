# NAT-004 — Static NAT maps 203

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/NAT/NAT-004/NAT-004.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: NAT
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: NAT misconfiguration
- Symptom: External users cannot reach the internal web server via public IP 203.0.113.10. Internal users can browse the web server at its private IP 10.10.10.15 without issues. [RED HERRING: An ACL on the external interface permits HTTP/HTTPS to 203.0.113.10 — rules look correct.]
- Topology note: R1 has static NAT configured for the web server. S0/0/0 (203.0.113.1/24) is the outside interface. Gi0/0.10 is the inside interface. ACL 180 is applied inbound on S0/0/0.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: Static NAT maps 203.0.113.10 to inside local address 10.10.10.50, but the actual web server's IP is 10.10.10.15. The NAT translation sends traffic to a non-existent host. The ACL correctly permits HTTP/HTTPS to the public IP — a red herring suggesting the ACL is the issue when it actually has zero matches because NAT is translating to the wrong host.
- Expected symptom: External users cannot reach the internal web server via public IP 203.0.113.10. Internal users can browse the web server at its private IP 10.10.10.15 without issues. [RED HERRING: An ACL on the external interface permits HTTP/HTTPS to 203.0.113.10 — rules look correct.]
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip nat translations
Pro Inside global       Inside local        Outside local      Outside global
--- 203.0.113.10        10.10.10.50         ---                ---

R1# show running-config | include nat
ip nat inside source static 10.10.10.50 203.0.113.10

R1# show access-lists
Extended IP access list 180
    10 permit tcp any host 203.0.113.10 eq 80 (0 matches)
    20 permit tcp any host 203.0.113.10 eq 443 (0 matches)
    30 deny   ip any any (45 matches)

R1# show ip interface Serial0/0/0
Serial0/0/0 is up, line protocol is up
  Ingoing access list is 180
  Outgoing access list is not set

R1# show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0.10      10.10.10.1      YES manual up                    up
Serial0/0/0                203.0.113.1     YES manual up                    up
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
