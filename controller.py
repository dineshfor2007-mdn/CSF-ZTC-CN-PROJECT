from config import SAFETY_LIMIT, MAX_TRANSFER
from digital_twin.digital_twin import DigitalTwin
from safety.safety_field import SafetyField


class NetworkController:
    def __init__(self, network):
        self.network = network
        self.digital_twin = DigitalTwin(network)
        self.safety = SafetyField()
        self.action_history = []

    def preview_actions(self, source):
        """Simulate possible traffic transfers without changing the network."""
        self.digital_twin.synchronize()
        candidates = []

        for destination in self.network.links:
            if destination == source:
                continue

            source_traffic = self.network.links[source]["traffic"]
            destination_link = self.network.links[destination]

            available_capacity = (
                destination_link["capacity"] * SAFETY_LIMIT / 100
                - destination_link["traffic"]
            )

            max_amount = min(
                MAX_TRANSFER,
                source_traffic,
                available_capacity,
            )

            amount = float(max_amount)

            if amount <= 0:
                continue

            simulated = self.digital_twin.simulate_transfer(
                source, destination, amount
            )

            if simulated is None:
                continue

            evaluation = self.safety.evaluate(simulated)

            if evaluation["safe"]:
                candidates.append({
                    "source": source,
                    "destination": destination,
                    "amount": amount,
                    "peak": evaluation["peak_utilization"],
                    "risk": evaluation["risk"],
                    "state": simulated,
                })

        return candidates

    def control_network(self):
        """Choose and apply the best safe action."""
        congested = [
            name for name, link in self.network.links.items()
            if link["traffic"] / link["capacity"] * 100 >= SAFETY_LIMIT
        ]

        if not congested:
            print("All links are below the safety limit. No action needed.")
            return False

        source = max(
            congested,
            key=lambda name: (
                self.network.links[name]["traffic"]
                / self.network.links[name]["capacity"]
            ),
        )

        print(f"\nMost congested link: {source}")
        candidates = self.preview_actions(source)

        if not candidates:
            print("No safe traffic-transfer action is available.")
            return False

        # Prefer lower peak utilization, then lower risk.
        best = min(
            candidates,
            key=lambda item: (item["peak"], item["risk"]),
        )

        # Recheck the selected action against the current network state.
        self.digital_twin.synchronize()
        projected = self.digital_twin.simulate_transfer(
            best["source"],
            best["destination"],
            best["amount"],
        )

        if projected is None or not self.safety.is_safe(projected):
            print("Safety validation failed. Action blocked.")
            return False

        self.network.transfer_traffic(
            best["source"],
            best["destination"],
            best["amount"],
        )

        self.action_history.append({
            "source": best["source"],
            "destination": best["destination"],
            "amount": best["amount"],
            "peak_before": max(
                self.network.utilization(name)
                for name in self.network.links
            ),
            "peak_projected": best["peak"],
            "risk_projected": best["risk"],
        })

        print(
            f"Safe action applied: moved {best['amount']:.1f} Mbps "
            f"from {best['source']} to {best['destination']}."
        )
        print(
            f"Projected peak utilization: {best['peak']:.1f}%"
        )
        return True