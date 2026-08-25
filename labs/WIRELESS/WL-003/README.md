# WL-003 — The trunk port Fa0/24 on SW1 (connecting to the AP) only allows VLANs 1 and 10 — VLAN 99 (Guest) is not in the allowed list

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/WIRELESS/WL-003/WL-003.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: WIRELESS
- Severity: High
- OSI layer: Layer 2 - Data Link
- Concept: Wireless/guest network issues
- Symptom: Guests connect to 'Guest-WiFi' and see 'connected' status but get APIPA addresses (169.254.x.x). Corporate SSID on the same AP works fine and clients get 10.10.10.x addresses. [RED HERRING: DHCP pool for VLAN 99 exists and is correctly configured on R1.]
- Topology note: AP1 connects to SW1 Fa0/24 (trunk). VLAN 99 (Guest) DHCP pool exists on R1. Corporate-WiFi (VLAN 10) works. AP1 serves both SSIDs.

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The trunk port Fa0/24 on SW1 (connecting to the AP) only allows VLANs 1 and 10 — VLAN 99 (Guest) is not in the allowed list. Guest-WiFi DHCP DISCOVERs tagged for VLAN 99 are dropped at the switch. The correctly configured DHCP pool on R1 is a red herring.
- Expected symptom: Guests connect to 'Guest-WiFi' and see 'connected' status but get APIPA addresses (169.254.x.x). Corporate SSID on the same AP works fine and clients get 10.10.10.x addresses. [RED HERRING: DHCP pool for VLAN 99 exists and is correctly configured on R1.]
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
R1# show ip dhcp pool

Pool GUEST-POOL :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 254
 Leased addresses               : 0
 Pending event                  : none
 1 subnet is currently in the pool :
 Current index        IP address range                    Leased addresses
 10.10.99.1           10.10.99.1       - 10.10.99.254    0

R1# show running-config | section dhcp
ip dhcp pool GUEST-POOL
 network 10.10.99.0 255.255.255.0
 default-router 10.10.99.1
 dns-server 8.8.8.8

SW1# show interfaces Fa0/24 trunk
Port        Mode         Encapsulation  Status        Native vlan
Fa0/24      on           802.1q         trunking      1

Port        Vlans allowed on trunk
Fa0/24      1,10

Port        Vlans allowed and active in management domain
Fa0/24      1,10

R1# show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0.10      10.10.10.1      YES manual up                    up
GigabitEthernet0/0.99      10.10.99.1      YES manual up                    up
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
