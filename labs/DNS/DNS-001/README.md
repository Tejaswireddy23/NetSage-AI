# DNS-001 — DHCP pool distributes the wrong DNS server address — 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/DNS/DNS-001/DNS-001.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: DNS
- Severity: Medium
- OSI layer: Layer 7 - Application
- Concept: DNS issues
- Symptom: PCs can ping 8.8.8.8 and all internal servers by IP, but browsing to www.corporate.local or any hostname fails. nslookup times out.
- Topology note: R1 is the DHCP server for VLAN 10 (10.10.10.0/24). A DNS server runs at 10.10.10.5 on Fa0/20 of SW1. DHCP pushes DNS settings to clients.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: DHCP pool distributes the wrong DNS server address — 10.10.10.50 (non-existent) instead of 10.10.10.5 (the actual DNS server). Clients send DNS queries to a host that does not exist.
- Expected symptom: PCs can ping 8.8.8.8 and all internal servers by IP, but browsing to www.corporate.local or any hostname fails. nslookup times out.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show running-config | section dhcp
ip dhcp pool VLAN10-POOL
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1
 dns-server 10.10.10.50

C:\> ipconfig /all
Ethernet adapter Ethernet0:
   IPv4 Address. . . . . . . . . : 10.10.10.11
   Subnet Mask . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . : 10.10.10.1
   DNS Servers . . . . . . . . . : 10.10.10.50

C:\> ping 10.10.10.5
Reply from 10.10.10.5: bytes=32 time<1ms TTL=128
Reply from 10.10.10.5: bytes=32 time<1ms TTL=128
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
