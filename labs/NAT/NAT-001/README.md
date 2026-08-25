# NAT-001 — The interfaces are not designated as NAT inside or NAT outside (ip nat inside / ip nat outside commands are missing from both interface configurations)

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/NAT/NAT-001/NAT-001.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: NAT
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: NAT misconfiguration
- Symptom: Internal PCs (10.10.10.0/24) cannot reach any internet site. Inter-VLAN routing between 10.10.10.0/24 and 10.10.20.0/24 works correctly. The serial link to the ISP is up.
- Topology note: R1 has Gi0/0.10 (10.10.10.1/24, internal) and S0/0/0 (209.165.200.225/30, external to ISP). PAT (overload) is configured.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The interfaces are not designated as NAT inside or NAT outside (ip nat inside / ip nat outside commands are missing from both interface configurations). NAT cannot function without these designations, so no translations are created.
- Expected symptom: Internal PCs (10.10.10.0/24) cannot reach any internet site. Inter-VLAN routing between 10.10.10.0/24 and 10.10.20.0/24 works correctly. The serial link to the ISP is up.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip nat translations
(no translations found)

R1# show ip nat statistics
Total active translations: 0
Outside interfaces: (none)
Inside interfaces: (none)
Hits: 0  Misses: 0

R1# show running-config | include nat
ip nat inside source list 1 interface Serial0/0/0 overload
access-list 1 permit 10.10.10.0 0.0.0.255

R1# show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0.10      10.10.10.1      YES manual up                    up
Serial0/0/0                209.165.200.225 YES manual up                    up

R1# show running-config interface GigabitEthernet0/0.10
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.10.10.1 255.255.255.0

R1# show running-config interface Serial0/0/0
interface Serial0/0/0
 ip address 209.165.200.225 255.255.255.252
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
