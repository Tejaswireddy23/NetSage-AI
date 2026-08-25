# WL-002 — Client isolation (peer-to-peer blocking) is not enabled on the Guest-WiFi SSID — the config shows 'no peer-to-peer blocking'

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/WIRELESS/WL-002/WL-002.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: WIRELESS
- Severity: Medium
- OSI layer: Layer 2 - Data Link
- Concept: Wireless/guest network issues
- Symptom: Guest wireless clients connected to 'Guest-WiFi' can discover and ping other guest devices. The security policy requires client-to-client isolation on the guest network.
- Topology note: AP1 broadcasts 'Guest-WiFi' on VLAN 99. Guest clients get IPs via DHCP from R1 (10.10.99.0/24 pool). 8 guest devices are currently connected.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: Client isolation (peer-to-peer blocking) is not enabled on the Guest-WiFi SSID — the config shows 'no peer-to-peer blocking'. Guest clients can communicate directly with each other, violating the isolation security policy.
- Expected symptom: Guest wireless clients connected to 'Guest-WiFi' can discover and ping other guest devices. The security policy requires client-to-client isolation on the guest network.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
AP1# show dot11 associations

802.11 Client Stations on Dot11Radio0:
SSID [Guest-WiFi] :
MAC Address    IP address      Device        Name
00a0.c9f1.0001 10.10.99.10     PC-Wireless   Guest1
00a0.c9f1.0002 10.10.99.11     PC-Wireless   Guest2
00a0.c9f1.0003 10.10.99.12     PC-Wireless   Guest3

AP1# show running-config | section dot11
interface Dot11Radio0
 ssid Guest-WiFi
  vlan 99
  authentication open
  guest-mode
 no peer-to-peer blocking
 speed basic-1.0 2.0 5.5 11.0

Guest1> ping 10.10.99.11
Reply from 10.10.99.11: bytes=32 time=3ms TTL=128
Reply from 10.10.99.11: bytes=32 time=2ms TTL=128
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
