# VLAN-002 — Native VLAN mismatch on the trunk link between SW1 (native VLAN 1) and SW2 (native VLAN 99) causes untagged frames to be mishandled and management traffic to be dropped

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/VLAN/VLAN-002/VLAN-002.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: VLAN
- Severity: High
- OSI layer: Layer 2 - Data Link
- Concept: VLAN misconfiguration
- Symptom: All inter-VLAN traffic between SW1 and SW2 works for VLANs 10 and 20, but CDP errors appear in logs and management VLAN frames on the native VLAN are dropped intermittently between the two switches.
- Topology note: SW1 (Gi0/1 trunk) connected to SW2 (Gi0/1 trunk). VLANs 1, 10, 20 are in use. SW1 is configured with native VLAN 1; SW2 was recently reconfigured.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: Native VLAN mismatch on the trunk link between SW1 (native VLAN 1) and SW2 (native VLAN 99) causes untagged frames to be mishandled and management traffic to be dropped.
- Expected symptom: All inter-VLAN traffic between SW1 and SW2 works for VLANs 10 and 20, but CDP errors appear in logs and management VLAN frames on the native VLAN are dropped intermittently between the two switches.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
SW1# show interfaces trunk

Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1-4094

Port        Vlans allowed and active in management domain
Gi0/1       1,10,20

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       1,10,20

SW2# show interfaces trunk

Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      99

Port        Vlans allowed on trunk
Gi0/1       1-4094

Port        Vlans allowed and active in management domain
Gi0/1       1,10,20,99

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       1,10,20,99

%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (1) with SW1 GigabitEthernet0/1 (99).
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
