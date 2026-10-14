import json
import os


class NetworkModel:
    def __init__(self, data_file="data/network.json"):
        self.data_file = data_file
        self.links = {}
        self.load_network()

    def load_network(self):
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(
                f"Network data file not found: {self.data_file}"
            )

        with open(self.data_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.links = data["links"]

    def utilization(self, link_name):
        link = self.links[link_name]
        return link["traffic"] / link["capacity"] * 100

    def all_utilization(self):
        return {
            name: self.utilization(name)
            for name in self.links
        }

    def peak_utilization(self):
        return max(self.all_utilization().values())

    def average_utilization(self):
        values = list(self.all_utilization().values())
        return sum(values) / len(values)

    def congested_links(self, safety_limit=80.0):
        return [
            name for name in self.links
            if self.utilization(name) >= safety_limit
        ]

    def get_state(self):
        return {
            name: link.copy()
            for name, link in self.links.items()
        }

    def set_state(self, state):
        self.links = {
            name: link.copy()
            for name, link in state.items()
        }

    def transfer_traffic(self, source, destination, amount):
        if source not in self.links or destination not in self.links:
            raise ValueError("Unknown source or destination link.")

        if source == destination:
            raise ValueError("Source and destination must differ.")

        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")

        if self.links[source]["traffic"] < amount:
            raise ValueError("Source does not have enough traffic.")

        self.links[source]["traffic"] -= amount
        self.links[destination]["traffic"] += amount

    def display(self, safety_limit=80.0):
        print("\nNETWORK STATUS")
        print("-" * 75)

        for name, link in self.links.items():
            usage = self.utilization(name)

            if usage >= 90:
                status = "CRITICAL"
            elif usage >= safety_limit:
                status = "CONGESTED"
            elif usage >= 70:
                status = "WARNING"
            else:
                status = "SAFE"

            print(
                f"{name:<10} | "
                f"Traffic: {link['traffic']:5.1f} Mbps | "
                f"Capacity: {link['capacity']:5.1f} Mbps | "
                f"Usage: {usage:5.1f}% | {status}"
            )

        print("-" * 75)
        print(f"Peak utilization: {self.peak_utilization():.1f}%")
        print(f"Average utilization: {self.average_utilization():.1f}%")