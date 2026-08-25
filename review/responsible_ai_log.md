# Responsible AI Review Log — NetSage

> Generated on **2026-08-14** by `review/log_reviews.py`

## Summary

| Metric | Value |
|---|---|
| Total cases reviewed | 36 |
| Accepted (AI correct) | 26 |
| Edited (partially correct) | 7 |
| Rejected (AI wrong) | 3 |
| Not yet reviewed | 0 |
| **Agreement rate** | **26/36 (72.2%)** |

> [!WARNING]
> Agreement rate of 72.2% — AI diagnoses need human verification before action.

---

## Cases Requiring Correction

Each entry below documents a case where the AI diagnosis was **Edited** or **Rejected** by a human reviewer, along with an analysis of *why* the AI likely produced an incorrect result.

### VLAN-005 — 🟡 Edited

| Field | Detail |
|---|---|
| **AI said** | The interface Fa0/12 on SW1 is configured as a trunk port, but it should be an access port in VLAN 10 to allow the PC to get a DHCP address and have connectivity |
| **Correct diagnosis** | VLAN 20 is not assigned to interface Fa0/2. |
| **Decision** | Edited |
| **Concept area** | VLAN misconfiguration |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI identified the issue as routing, but it was just a missing switchport access vlan command.

---

### GW-005 — 🔴 Rejected

| Field | Detail |
|---|---|
| **AI said** | IP routing is disabled on MLS1, preventing it from routing traffic between VLANs 10 and 20 |
| **Correct diagnosis** | Default gateway is configured correctly on the PC, but the switch SVI is down. |
| **Decision** | Rejected |
| **Concept area** | Default gateway issues |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI blamed the gateway IP itself, but the gateway interface is administratively down.

---

### DHCP-004 — 🟡 Edited

| Field | Detail |
|---|---|
| **AI said** | DHCP excluded-address range 10.10.10.1–10.10.10.250 is overly broad, leaving only 4 usable addresses (.251–.254); the pool's 'Total addresses: 254' is misleading because the exclusion negates nearly all of them |
| **Correct diagnosis** | DHCP pool is exhausted because of excluded addresses, not total size. |
| **Decision** | Edited |
| **Concept area** | DHCP failures |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI said the pool was large enough, completely missing the ip dhcp excluded-address range.

---

### DNS-002 — 🔴 Rejected

| Field | Detail |
|---|---|
| **AI said** | ACL 120 on R1's Gi0/0.10 sub-interface blocks incoming UDP DNS requests (deny udp any any eq 53), preventing PCs from resolving names despite having the correct DNS server IP |
| **Correct diagnosis** | DNS server address provided via DHCP is incorrect. |
| **Decision** | Rejected |
| **Concept area** | DNS issues |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI said DNS was reachable, but the IP handed out to clients is wrong.

---

### DNS-004 — 🔴 Rejected

| Field | Detail |
|---|---|
| **AI said** | The DNS server (10.10.10.5) has an incomplete ARP entry on R1, indicating that R1 has not received an ARP response from the DNS server, likely due to the DNS server not sending ARP replies or a Layer 2 issue |
| **Correct diagnosis** | Host has no route to the external DNS server. |
| **Decision** | Rejected |
| **Concept area** | DNS issues |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI focused on DNS server availability instead of basic reachability/routing.

---

### RT-004 — 🟡 Edited

| Field | Detail |
|---|---|
| **AI said** | OSPF area mismatch between R1 and R2: R1 is configured for Area 0 while R2 is configured for Area 1, preventing neighbor adjacency formation |
| **Correct diagnosis** | Missing static route for the 10.1.2.0/24 network. |
| **Decision** | Edited |
| **Concept area** | Routing |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI pointed out a trunk issue, but the routing table is actually missing the route.

---

### NAT-004 — 🟡 Edited

| Field | Detail |
|---|---|
| **AI said** | nan |
| **Correct diagnosis** | NAT pool exhaustion; no IP addresses left in the NAT pool. |
| **Decision** | Edited |
| **Concept area** | NAT misconfiguration |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI timed out or failed to provide a diagnosis, but the NAT pool was clearly exhausted.

---

### WL-001 — 🟡 Edited

| Field | Detail |
|---|---|
| **AI said** | nan |
| **Correct diagnosis** | The 'Guest-WiFi' SSID is mapped to VLAN 10 (Corporate) instead of VLAN 99 (Guest). Guest users are placed directly on the corporate network with full access to internal resources. |
| **Decision** | Edited |
| **Concept area** | Wireless/guest network issues |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI failed to provide a response due to API rate limits.

---

### WL-002 — 🟡 Edited

| Field | Detail |
|---|---|
| **AI said** | nan |
| **Correct diagnosis** | Client isolation (peer-to-peer blocking) is not enabled on the Guest-WiFi SSID — the config shows 'no peer-to-peer blocking'. Guest clients can communicate directly with each other, violating the isolation security policy. |
| **Decision** | Edited |
| **Concept area** | Wireless/guest network issues |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI failed to provide a response due to API rate limits.

---

### WL-003 — 🟡 Edited

| Field | Detail |
|---|---|
| **AI said** | nan |
| **Correct diagnosis** | The trunk port Fa0/24 on SW1 (connecting to the AP) only allows VLANs 1 and 10 — VLAN 99 (Guest) is not in the allowed list. Guest-WiFi DHCP DISCOVERs tagged for VLAN 99 are dropped at the switch. The correctly configured DHCP pool on R1 is a red herring. |
| **Decision** | Edited |
| **Concept area** | Wireless/guest network issues |
| **Reviewer** | Tharun |
| **Review date** | 2026-08-14 |

**Why the AI likely got it wrong:**
AI failed to provide a response due to API rate limits.

---

## Observed Error Patterns

| Concept Area | Correction Count |
|---|---|
| Wireless/guest network issues | 3 |
| DNS issues | 2 |
| VLAN misconfiguration | 1 |
| Default gateway issues | 1 |
| DHCP failures | 1 |
| Routing | 1 |
| NAT misconfiguration | 1 |

> [!IMPORTANT]
> The AI struggled most with **Wireless/guest network issues** cases (3 correction(s)). Consider adding more few-shot examples for this category in `prompts/diagnose_prompt.md`.
