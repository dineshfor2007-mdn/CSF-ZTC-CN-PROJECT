class DigitalTwin:
    def __init__(self, network):
        self.network = network
        self.state = network.get_state()

    def synchronize(self):
        self.state = self.network.get_state()

    def simulate_transfer(self, source, destination, amount):
        simulated = {
            name: link.copy()
            for name, link in self.state.items()
        }

        if source not in simulated or destination not in simulated:
            return None

        if source == destination or amount <= 0:
            return None

        if simulated[source]["traffic"] < amount:
            return None

        simulated[source]["traffic"] -= amount
        simulated[destination]["traffic"] += amount

        return simulated

    @staticmethod
    def calculate_utilization(state):
        return {
            name: link["traffic"] / link["capacity"] * 100
            for name, link in state.items()
        }

    def peak_utilization(self, state):
        values = self.calculate_utilization(state).values()
        return max(values)

    def average_utilization(self, state):
        values = list(self.calculate_utilization(state).values())
        return sum(values) / len(values)