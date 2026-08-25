# WL-001 — The 'Guest-WiFi' SSID is mapped to VLAN 10 (Corporate) instead of VLAN 99 (Guest)

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/WIRELESS/WL-001/WL-001.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: WIRELESS
- Severity: Critical
- OSI layer: Layer 2 - Data Link
- Concept: Wireless/guest network issues
- Symptom: Guests connecting to the 'Guest-WiFi' SSID are able to browse internal corporate file shares and access sensitive servers on VLAN 10 (Corporate). The security policy requires guest isolation to internet-only access.
- Topology note: AP1 (Cisco Lightweight AP or autonomous AP in Packet Tracer) broadcasts two SSIDs: 'Corporate-WiFi' mapped to VLAN 10 and 'Guest-WiFi'. AP1 uplink on SW1 Fa0/24 is a trunk. VLAN 10 = Corporate (10.10.10.0/24), VLAN 99 = Guest (10.10.99.0/24).

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The 'Guest-WiFi' SSID is mapped to VLAN 10 (Corporate) instead of VLAN 99 (Guest). Guest users are placed directly on the corporate network with full access to internal resources.
- Expected symptom: Guests connecting to the 'Guest-WiFi' SSID are able to browse internal corporate file shares and access sensitive servers on VLAN 10 (Corporate). The security policy requires guest isolation to internet-only access.
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
SW1# show interfaces Fa0/24 trunk
Port        Mode         Encapsulation  Status        Native vlan
Fa0/24      on           802.1q         trunking      1

Port        Vlans allowed on trunk
Fa0/24      1,10,99

Port        Vlans allowed and active in management domain
Fa0/24      1,10,99

AP Configuration Summary:
SSID: Corporate-WiFi
  VLAN: 10
  Security: WPA2-Enterprise
SSID: Guest-WiFi
  VLAN: 10
  Security: WPA2-PSK

SW1# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/22, Fa0/23
10   Corporate                        active    Fa0/1, Fa0/2, Fa0/3
99   Guest                            active
1002 fddi-default                     act/unsup
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
