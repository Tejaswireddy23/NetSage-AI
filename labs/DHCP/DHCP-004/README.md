# DHCP-004 — The DHCP excluded-address range 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/DHCP/DHCP-004/DHCP-004.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: DHCP
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: DHCP failures
- Symptom: Only 5 PCs on VLAN 10 (10.10.10.0/24) successfully get DHCP addresses. The 6th PC and onward get APIPA despite the pool showing total addresses as 254. [RED HERRING: pool size appears correct at 254 addresses.]
- Topology note: R1 is the DHCP server for VLAN 10. An administrator recently added a broad exclusion range as a 'security measure'. 30 PCs need addresses.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The DHCP excluded-address range 10.10.10.1 through 10.10.10.250 is overly broad, leaving only 4 usable addresses (.251-.254). The pool's total of 254 addresses is a red herring — the exclusion negates nearly all of them.
- Expected symptom: Only 5 PCs on VLAN 10 (10.10.10.0/24) successfully get DHCP addresses. The 6th PC and onward get APIPA despite the pool showing total addresses as 254. [RED HERRING: pool size appears correct at 254 addresses.]
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip dhcp pool

Pool VLAN10-POOL :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 254
 Leased addresses               : 5
 Pending event                  : none
 1 subnet is currently in the pool :
 Current index        IP address range                    Leased addresses
 10.10.10.255         10.10.10.1       - 10.10.10.254    5

R1# show running-config | section dhcp
ip dhcp excluded-address 10.10.10.1 10.10.10.250
ip dhcp pool VLAN10-POOL
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1
 dns-server 10.10.10.5

R1# show ip dhcp binding
IP address       Client-ID/              Lease expiration        Type
                 Hardware address
10.10.10.251     0100.1a2b.3c01          Aug 09 2026 08:00 AM    Automatic
10.10.10.252     0100.1a2b.3c02          Aug 09 2026 08:01 AM    Automatic
10.10.10.253     0100.1a2b.3c03          Aug 09 2026 08:02 AM    Automatic
10.10.10.254     0100.1a2b.3c04          Aug 09 2026 08:03 AM    Automatic
10.10.10.250     0100.1a2b.3c05          Aug 09 2026 08:04 AM    Automatic
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
