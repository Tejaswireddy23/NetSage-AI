# VLAN-003 — VLAN 50 is not in the allowed VLAN list on the trunk port Gi0/1 (only VLANs 1, 10, 20 are allowed), so VLAN 50 traffic cannot cross between SW1 and SW2

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/VLAN/VLAN-003/VLAN-003.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: VLAN
- Severity: High
- OSI layer: Layer 2 - Data Link
- Concept: VLAN misconfiguration
- Symptom: PCs in VLAN 50 (Engineering) on SW2 cannot reach the Engineering file server in VLAN 50 on SW1, but PCs in VLAN 10 and 20 on SW2 reach their servers on SW1 without issues.
- Topology note: SW1 trunk Gi0/1 to SW2 trunk Gi0/1. VLAN 50 (Engineering, 10.10.50.0/24) was recently added. File server on SW1 Fa0/15 in VLAN 50.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: VLAN 50 is not in the allowed VLAN list on the trunk port Gi0/1 (only VLANs 1, 10, 20 are allowed), so VLAN 50 traffic cannot cross between SW1 and SW2.
- Expected symptom: PCs in VLAN 50 (Engineering) on SW2 cannot reach the Engineering file server in VLAN 50 on SW1, but PCs in VLAN 10 and 20 on SW2 reach their servers on SW1 without issues.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
SW1# show interfaces Gi0/1 trunk

Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1,10,20

Port        Vlans allowed and active in management domain
Gi0/1       1,10,20

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       1,10,20

SW1# show vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/22, Fa0/23, Fa0/24
10   Sales                            active    Fa0/1, Fa0/2, Fa0/3
20   HR                               active    Fa0/6, Fa0/7, Fa0/8
50   Engineering                      active    Fa0/15, Fa0/16
1002 fddi-default                     act/unsup
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
