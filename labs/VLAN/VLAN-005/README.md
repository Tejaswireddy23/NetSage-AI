# VLAN-005 — Port Fa0/12 is configured as a trunk port instead of an access port in VLAN 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/VLAN/VLAN-005/VLAN-005.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: VLAN
- Severity: Medium
- OSI layer: Layer 2 - Data Link
- Concept: VLAN misconfiguration
- Symptom: PC on Fa0/12 of SW1 cannot get a DHCP address and has no connectivity. The link LED is solid green. Other PCs on VLAN 10 work fine. [RED HERRING: an ACL is present on R1 but permits the relevant traffic.]
- Topology note: SW1 Fa0/12 connects a new PC for the Sales team (VLAN 10). R1 performs router-on-a-stick routing. An inbound ACL 110 exists on R1's Gi0/0.10 subinterface.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: Port Fa0/12 is configured as a trunk port instead of an access port in VLAN 10. The PC cannot interpret 802.1Q-tagged frames and fails to communicate. The ACL on R1 is a red herring — it correctly permits VLAN 10 traffic.
- Expected symptom: PC on Fa0/12 of SW1 cannot get a DHCP address and has no connectivity. The link LED is solid green. Other PCs on VLAN 10 work fine. [RED HERRING: an ACL is present on R1 but permits the relevant traffic.]
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
SW1# show interfaces Fa0/12 switchport
Name: Fa0/12
Switchport: Enabled
Administrative Mode: trunk
Operational Mode: trunk
Administrative Trunking Encapsulation: dot1q
Negotiation of Trunking: On
Trunking Native Mode VLAN: 1 (default)
Trunking VLANs Enabled: ALL

SW1# show vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/22, Fa0/23, Fa0/24
10   Sales                            active    Fa0/1, Fa0/2, Fa0/3
20   HR                               active    Fa0/6, Fa0/7, Fa0/8
1002 fddi-default                     act/unsup

R1# show access-lists
Extended IP access list 110
    10 permit ip 10.10.10.0 0.0.0.255 any (385 matches)
    20 permit ip any 10.10.10.0 0.0.0.255 (220 matches)
    30 deny   ip any any
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
