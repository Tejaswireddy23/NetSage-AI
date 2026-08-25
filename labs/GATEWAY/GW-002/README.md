# GW-002 — Router subinterface Gi0/0

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/GATEWAY/GW-002/GW-002.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: GATEWAY
- Severity: High
- OSI layer: Layer 3 - Network
- Concept: Default gateway issues
- Symptom: All PCs on VLAN 10 (10.10.10.0/24) can ping each other but cannot reach VLAN 20 or the internet. PCs on VLAN 20 can reach the internet fine.
- Topology note: R1 provides router-on-a-stick routing via Gi0/0 subinterfaces. Gi0/0.10 serves VLAN 10 and Gi0/0.20 serves VLAN 20. Trunk link from SW1 Gi0/1 to R1 Gi0/0.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: Router subinterface Gi0/0.10 is administratively down (shutdown), so R1 cannot serve as the gateway for VLAN 10. VLAN 20 works because Gi0/0.20 is up/up.
- Expected symptom: All PCs on VLAN 10 (10.10.10.0/24) can ping each other but cannot reach VLAN 20 or the internet. PCs on VLAN 20 can reach the internet fine.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         unassigned      YES unset  up                    up
GigabitEthernet0/0.10      10.10.10.1      YES manual administratively down down
GigabitEthernet0/0.20      10.10.20.1      YES manual up                    up
Serial0/0/0                209.165.200.225 YES manual up                    up

R1# show interfaces GigabitEthernet0/0.10
GigabitEthernet0/0.10 is administratively down, line protocol is down
  Hardware is iGbE, address is 0019.aa6b.3401
  Internet address is 10.10.10.1/24
  Encapsulation 802.1Q Virtual LAN, Vlan ID  10.
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
