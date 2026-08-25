# VLAN-001 — Port Fa0/5 is assigned to VLAN 30 (Marketing) instead of VLAN 20 (Accounting), so PC3 is in the wrong broadcast domain and cannot reach VLAN 20 resources

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/VLAN/VLAN-001/VLAN-001.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: VLAN
- Severity: Medium
- OSI layer: Layer 2 - Data Link
- Concept: VLAN misconfiguration
- Symptom: PC3 in Accounting (Fa0/5 on SW1) cannot reach the file server on Fa0/20; all other Accounting PCs on the same switch communicate normally.
- Topology note: SW1 is a Cisco 2960 with VLAN 20 (Accounting, 10.10.20.0/24) and VLAN 30 (Marketing, 10.10.30.0/24). File server is on Fa0/20 in VLAN 20. PC3 is on Fa0/5.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: Port Fa0/5 is assigned to VLAN 30 (Marketing) instead of VLAN 20 (Accounting), so PC3 is in the wrong broadcast domain and cannot reach VLAN 20 resources.
- Expected symptom: PC3 in Accounting (Fa0/5 on SW1) cannot reach the file server on Fa0/20; all other Accounting PCs on the same switch communicate normally.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
SW1# show vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/22, Fa0/23, Fa0/24
20   Accounting                       active    Fa0/1, Fa0/2, Fa0/3, Fa0/4,
                                                Fa0/20
30   Marketing                        active    Fa0/5, Fa0/6, Fa0/7, Fa0/8
99   Management                       active
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup

SW1# show interfaces Fa0/5 switchport
Name: Fa0/5
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Negotiation of Trunking: Off
Access Mode VLAN: 30 (Marketing)
Trunking Native Mode VLAN: 1 (default)
Voice VLAN: none
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
