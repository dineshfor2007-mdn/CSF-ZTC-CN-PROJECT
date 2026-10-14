import os
import logging

from config import PROJECT_NAME, SAFETY_LIMIT, LOG_FILE
from network.network_model import NetworkModel
from digital_twin.learning import OnlineLearning
from safety.safety_field import SafetyField
from controller.controller import NetworkController


def main():
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    print("=" * 65)
    print(PROJECT_NAME)
    print("Counterfactual Safety-Aware Network Traffic Control")
    print("=" * 65)

    # Load the simulated network.
    network = NetworkModel()
    learning = OnlineLearning()
    safety = SafetyField(SAFETY_LIMIT)
    controller = NetworkController(network)

    print("\nBEFORE CONTROL")
    network.display(SAFETY_LIMIT)

    initial_peak = network.peak_utilization()
    initial_risk = safety.calculate_risk(network.get_state())

    # Update the traffic history.
    learning.update(network)

    print("\nCOUNTERFACTUAL ANALYSIS")
    congested = network.congested_links(SAFETY_LIMIT)

    if congested:
        source = max(congested, key=network.utilization)
        candidates = controller.preview_actions(source)

        if candidates:
            for candidate in candidates:
                print(
                    f"What if {candidate['amount']:.1f} Mbps moves "
                    f"from {candidate['source']} to "
                    f"{candidate['destination']}? "
                    f"Projected peak: {candidate['peak']:.1f}% "
                    f"| Risk: {candidate['risk']:.3f} | SAFE"
                )
        else:
            print("No safe transfer candidates found.")
    else:
        print("No congested links detected.")

    print("\nAUTOMATIC CONTROL")
    action_applied = controller.control_network()

    print("\nAFTER CONTROL")
    network.display(SAFETY_LIMIT)

    final_peak = network.peak_utilization()
    final_risk = safety.calculate_risk(network.get_state())

    print("\nPERFORMANCE SUMMARY")
    print("-" * 40)
    print(f"Initial peak utilization: {initial_peak:.1f}%")
    print(f"Final peak utilization:   {final_peak:.1f}%")
    print(f"Peak improvement:         {initial_peak - final_peak:.1f} percentage points")
    print(f"Initial risk score:       {initial_risk:.3f}")
    print(f"Final risk score:         {final_risk:.3f}")
    print(f"Safety limit:             {SAFETY_LIMIT:.1f}%")
    print(f"Action applied:           {'Yes' if action_applied else 'No'}")

    logging.info(
        "Control cycle complete. Initial peak %.2f%%, final peak %.2f%%",
        initial_peak,
        final_peak,
    )

    print("\nProject run completed.")


if __name__ == "__main__":
    main()