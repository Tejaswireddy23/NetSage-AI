# NAT-003 — NAT pool NATPOOL contains only 4 public IP addresses (209

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/NAT/NAT-003/NAT-003.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: NAT
- Severity: Medium
- OSI layer: Layer 3 - Network
- Concept: NAT misconfiguration
- Symptom: Internet works for most users but during peak hours (30+ concurrent users), some PCs get 'destination unreachable' when trying to browse. It works again if they retry after a few minutes.
- Topology note: R1 uses a NAT pool (NATPOOL) with a small range of public IPs for PAT. S0/0/0 is the outside interface. About 50 users are active.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: NAT pool NATPOOL contains only 4 public IP addresses (209.165.200.225-228) with non-overload (one-to-one) mapping. When all 4 are allocated, additional translations fail (312 misses). The pool should use overload (PAT) or be expanded.
- Expected symptom: Internet works for most users but during peak hours (30+ concurrent users), some PCs get 'destination unreachable' when trying to browse. It works again if they retry after a few minutes.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip nat statistics
Total active translations: 4
Peak translations: 4, occurred 14:32:10 ago
Outside interfaces:
  Serial0/0/0
Inside interfaces:
  GigabitEthernet0/0.10, GigabitEthernet0/0.20
Hits: 12840  Misses: 312
Expired translations: 8200
Dynamic mappings:
-- Inside Source
[Id: 1] access-list 10 pool NATPOOL refcount 4
 pool NATPOOL: netmask 255.255.255.252
        start 209.165.200.225 end 209.165.200.228
        type generic, total addresses 4, allocated 4 (100%), misses 312

R1# show ip nat translations
Pro Inside global       Inside local        Outside local      Outside global
tcp 209.165.200.225:1024 10.10.10.11:5000   93.184.216.34:80   93.184.216.34:80
tcp 209.165.200.226:1024 10.10.10.12:5001   93.184.216.34:443  93.184.216.34:443
tcp 209.165.200.227:1024 10.10.20.15:3000   8.8.8.8:443        8.8.8.8:443
tcp 209.165.200.228:1024 10.10.20.20:4000   1.1.1.1:80         1.1.1.1:80
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
