from network.network_model import NetworkModel
from digital_twin.digital_twin import DigitalTwin
from safety.safety_field import SafetyField


def test_network_loads():
    network = NetworkModel()
    assert len(network.links) == 4


def test_link_a_utilization():
    network = NetworkModel()
    assert network.utilization("Link A") == 60.0


def test_link_c_is_congested():
    network = NetworkModel()
    assert "Link C" in network.congested_links(80.0)


def test_digital_twin_does_not_change_network():
    network = NetworkModel()
    before = network.get_state()

    twin = DigitalTwin(network)
    simulated = twin.simulate_transfer("Link C", "Link A", 5)

    assert simulated is not None
    assert network.get_state() == before
    assert simulated["Link C"]["traffic"] == 22
    assert simulated["Link A"]["traffic"] == 35


def test_safety_accepts_safe_state():
    network = NetworkModel()
    twin = DigitalTwin(network)
    safety = SafetyField()

    simulated = twin.simulate_transfer("Link C", "Link A", 5)

    assert safety.is_safe(simulated)


def test_safety_rejects_unsafe_state():
    network = NetworkModel()
    twin = DigitalTwin(network)
    safety = SafetyField()

    simulated = twin.simulate_transfer("Link C", "Link B", 10)

    assert not safety.is_safe(simulated)