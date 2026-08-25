# DNS-004 — The DNS server at 10

## Lab status

**REQUIRES PACKET TRACER.** Create and save `labs/DNS/DNS-004/DNS-004.pkt` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: DNS
- Severity: Critical
- OSI layer: Layer 1 - Physical
- Concept: DNS issues
- Symptom: All PCs report DNS failures — browsing and nslookup time out. Pinging the DNS server 10.10.10.5 returns 'Request timed out'. The switch port for the DNS server is up. [RED HERRING: Switch port Fa0/20 is up/up and in correct VLAN.]
- Topology note: DNS server is connected to SW1 Fa0/20 in VLAN 10. R1 is the gateway. PCs are in VLAN 10 (10.10.10.0/24).

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: The DNS server at 10.10.10.5 is powered off or its NIC is disconnected — ARP resolution for 10.10.10.5 shows 'Incomplete' on R1. The switch port being up/connected is a red herring (the port may be connected but the server's NIC or OS is not responding).
- Expected symptom: All PCs report DNS failures — browsing and nslookup time out. Pinging the DNS server 10.10.10.5 returns 'Request timed out'. The switch port for the DNS server is up. [RED HERRING: Switch port Fa0/20 is up/up and in correct VLAN.]
- Expected fix: REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.
- Verification commands: ['REQUIRES HUMAN INPUT: choose commands after building the topology']
- Expected verification result: NOT VERIFIED - requires Packet Tracer

## Source pre-fix evidence

```text
SW1# show interfaces Fa0/20 status
Port      Name       Status       Vlan       Duplex  Speed Type
Fa0/20    DNS-SRV    connected    10         a-full  a-100 10/100BaseTX

SW1# show vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
10   Sales                            active    Fa0/1, Fa0/2, Fa0/3, Fa0/20

R1# show arp
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  10.10.10.1              -   0019.aa6b.3401  ARPA   Gi0/0.10
Internet  10.10.10.11             8   00d0.ba12.3401  ARPA   Gi0/0.10
Internet  10.10.10.5              0   Incomplete      ARPA   Gi0/0.10

C:\> ping 10.10.10.5
Request timed out.
Request timed out.
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
