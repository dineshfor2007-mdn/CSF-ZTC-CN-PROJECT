from config import SAFETY_LIMIT, WARNING_LIMIT, CRITICAL_LIMIT


class SafetyField:
    def __init__(self, safety_limit=SAFETY_LIMIT):
        self.safety_limit = safety_limit

    def is_safe(self, state):
        """Return True only if every link is within the safety limit."""
        for link in state.values():
            usage = link["traffic"] / link["capacity"] * 100

            if usage > self.safety_limit:
                return False

        return True

    def calculate_risk(self, state):
        """Estimate risk using utilization, delay, and packet loss."""
        total_risk = 0.0

        for link in state.values():
            usage = link["traffic"] / link["capacity"] * 100
            delay = link.get("delay", 0)
            packet_loss = link.get("packet_loss", 0)

            utilization_risk = min(usage / 100, 1.5) * 60
            delay_risk = min(delay / 100, 1.0) * 25
            loss_risk = min(packet_loss / 5, 1.0) * 15

            total_risk += (
                utilization_risk + delay_risk + loss_risk
            ) / 100

        return total_risk / len(state) if state else 0.0

    def evaluate(self, state):
        """Return safety, risk, and utilization details."""
        utilizations = {
            name: link["traffic"] / link["capacity"] * 100
            for name, link in state.items()
        }

        peak = max(utilizations.values()) if utilizations else 0.0
        average = (
            sum(utilizations.values()) / len(utilizations)
            if utilizations else 0.0
        )

        return {
            "safe": self.is_safe(state),
            "risk": self.calculate_risk(state),
            "peak_utilization": peak,
            "average_utilization": average,
            "utilizations": utilizations,
        }

    def status(self, usage):
        if usage >= CRITICAL_LIMIT:
            return "CRITICAL"
        if usage >= self.safety_limit:
            return "CONGESTED"
        if usage >= WARNING_LIMIT:
            return "WARNING"
        return "SAFE"