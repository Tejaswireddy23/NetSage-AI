# DNS-003 — The DHCP pool is missing the dns-server option entirely

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/DNS/DNS-003/DNS-003.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: DNS
- Severity: Medium
- OSI layer: Layer 7 - Application
- Concept: DNS issues
- Symptom: PCs can ping every IP address including the DNS server and the gateway, but any name resolution (nslookup, browsing by hostname) fails. ipconfig /all shows no DNS server configured.
- Topology note: R1 is the DHCP server. DNS server is at 10.10.10.5 on VLAN 10. 10 PCs in VLAN 10.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The DHCP pool is missing the dns-server option entirely. PCs receive an IP and gateway via DHCP but no DNS server address, so all name resolution fails.
- Expected symptom: PCs can ping every IP address including the DNS server and the gateway, but any name resolution (nslookup, browsing by hostname) fails. ipconfig /all shows no DNS server configured.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show running-config | section dhcp
ip dhcp pool VLAN10-POOL
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1

R1# show ip dhcp binding
IP address       Client-ID/              Lease expiration        Type
                 Hardware address
10.10.10.11      0100.1a2b.3c01          Aug 09 2026 08:00 AM    Automatic
10.10.10.12      0100.1a2b.3c02          Aug 09 2026 08:01 AM    Automatic

C:\> ipconfig /all
Ethernet adapter Ethernet0:
   IPv4 Address. . . . . . . . . : 10.10.10.11
   Subnet Mask . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . : 10.10.10.1
   DNS Servers . . . . . . . . . :
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
