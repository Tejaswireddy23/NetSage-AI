# DNS-002 — ACL 120 on R1 Gi0/0

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/DNS/DNS-002/DNS-002.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: DNS
- Severity: High
- OSI layer: Layer 7 - Application
- Concept: DNS issues
- Symptom: nslookup fails from all PCs with 'request timed out'. Pinging the DNS server at 10.10.10.5 by IP address succeeds. [RED HERRING: DNS server IP in DHCP config is correct.]
- Topology note: R1 is the gateway and has ACL 120 applied inbound on Gi0/0.10. DNS server is at 10.10.10.5 on VLAN 10. DHCP correctly assigns dns-server 10.10.10.5.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: ACL 120 on R1 Gi0/0.10 explicitly denies UDP port 53 (line 40) before the permit-all on line 50, blocking DNS query traffic. The DHCP dns-server configuration is correct — a red herring that makes it appear the DNS setup is fine.
- Expected symptom: nslookup fails from all PCs with 'request timed out'. Pinging the DNS server at 10.10.10.5 by IP address succeeds. [RED HERRING: DNS server IP in DHCP config is correct.]
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show running-config | section dhcp
ip dhcp pool VLAN10-POOL
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1
 dns-server 10.10.10.5

R1# show access-lists
Extended IP access list 120
    10 permit icmp any any (1520 matches)
    20 permit tcp any any eq 80 (890 matches)
    30 permit tcp any any eq 443 (672 matches)
    40 deny   udp any any eq 53 (342 matches)
    50 permit ip any any (105 matches)

R1# show ip interface GigabitEthernet0/0.10
GigabitEthernet0/0.10 is up, line protocol is up
  Ingoing access list is 120
  Outgoing access list is not set
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
