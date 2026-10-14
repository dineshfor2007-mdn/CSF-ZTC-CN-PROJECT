import random


class TrafficGenerator:
    def __init__(self, variation=0.15):
        self.variation = variation

    def generate(self, network):
        for link in network.links.values():
            change = random.uniform(
                -self.variation,
                self.variation
            )

            new_traffic = link["traffic"] * (1 + change)

            link["traffic"] = max(
                0.0,
                min(new_traffic, link["capacity"])
            )

        return network