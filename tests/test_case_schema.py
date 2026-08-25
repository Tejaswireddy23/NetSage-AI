from data.case_schema import normalise_case, parse_list


def test_legacy_case_is_backward_compatible():
    case = normalise_case({
        "case_id": "GW-001", "symptom": "x", "topology_note": "y",
        "show_output": "z", "expected_fault": "Gateway issue.",
        "osi_layer": "Layer 3 - Network", "concept_tag": "gateway", "severity": "High",
    })
    assert case["category"] == "GATEWAY"
    assert case["expected_fix"] == []
    assert case["title"] == "Gateway issue"


def test_json_list_fields_are_parsed():
    assert parse_list('["show vlan brief", "ping 10.0.0.1"]') == ["show vlan brief", "ping 10.0.0.1"]
