# NAT-002 — NAT access list 10 only permits the 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/NAT/NAT-002/NAT-002.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: NAT
- Severity: Medium
- OSI layer: Layer 3 - Network
- Concept: NAT misconfiguration
- Symptom: PCs on 10.10.10.0/24 (VLAN 10) can reach the internet. PCs on 10.10.20.0/24 (VLAN 20) cannot reach any internet site, though they can reach all internal networks including VLAN 10.
- Topology note: R1 performs PAT via S0/0/0 to ISP. Gi0/0.10 and Gi0/0.20 are inside interfaces. NAT ACL controls which source networks are translated.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: NAT access list 10 only permits the 10.10.10.0/24 network. The 10.10.20.0/24 network is not included, so VLAN 20 traffic is never translated and is dropped at the ISP edge.
- Expected symptom: PCs on 10.10.10.0/24 (VLAN 10) can reach the internet. PCs on 10.10.20.0/24 (VLAN 20) cannot reach any internet site, though they can reach all internal networks including VLAN 10.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip nat translations
Pro Inside global       Inside local        Outside local      Outside global
tcp 209.165.200.225:1024 10.10.10.11:1025   8.8.8.8:80         8.8.8.8:80
tcp 209.165.200.225:1025 10.10.10.12:1026   8.8.4.4:443        8.8.4.4:443

R1# show running-config | include nat
ip nat inside source list 10 interface Serial0/0/0 overload

R1# show access-lists
Standard IP access list 10
    10 permit 10.10.10.0, wildcard bits 0.0.0.255 (285 matches)

R1# show running-config interface GigabitEthernet0/0.10
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.10.10.1 255.255.255.0
 ip nat inside

R1# show running-config interface GigabitEthernet0/0.20
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.10.20.1 255.255.255.0
 ip nat inside

R1# show running-config interface Serial0/0/0
interface Serial0/0/0
 ip address 209.165.200.225 255.255.255.252
 ip nat outside
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
