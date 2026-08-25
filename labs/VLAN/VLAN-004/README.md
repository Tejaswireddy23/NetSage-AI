# VLAN-004 — VLAN 40 has not been created on SW2 (it does not appear in show vlan brief), so the port is assigned to a non-existent VLAN and all traffic is dropped

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/VLAN/VLAN-004/VLAN-004.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: VLAN
- Severity: High
- OSI layer: Layer 2 - Data Link
- Concept: VLAN misconfiguration
- Symptom: PC on Fa0/10 of SW2 has no network connectivity at all — link light is green, PC shows 'cable connected' but gets an APIPA address.
- Topology note: SW2 is a 2960 switch. Fa0/10 was supposed to be in VLAN 40 (Guest, 10.10.40.0/24). Router-on-a-stick R1 provides inter-VLAN routing on Gi0/0 subinterfaces.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: VLAN 40 has not been created on SW2 (it does not appear in show vlan brief), so the port is assigned to a non-existent VLAN and all traffic is dropped.
- Expected symptom: PC on Fa0/10 of SW2 has no network connectivity at all — link light is green, PC shows 'cable connected' but gets an APIPA address.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
SW2# show vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/22, Fa0/23, Fa0/24
10   Sales                            active    Fa0/1, Fa0/2, Fa0/3
20   HR                               active    Fa0/6, Fa0/7, Fa0/8
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup

SW2# show interfaces Fa0/10 switchport
Name: Fa0/10
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Access Mode VLAN: 40 (!)
Trunking Native Mode VLAN: 1 (default)

SW2# show interfaces Fa0/10 status
Port      Name    Status       Vlan       Duplex  Speed Type
Fa0/10            connected    40         a-full  a-100 10/100BaseTX
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
