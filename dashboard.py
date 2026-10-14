import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from network.network_model import NetworkModel
from digital_twin.digital_twin import DigitalTwin
from safety.safety_field import SafetyField
from controller.controller import NetworkController


st.set_page_config(
    page_title="CSF-ZTC Network Dashboard",
    page_icon="🌐",
    layout="wide",
)

st.title("CSF-ZTC Network Control Dashboard")
st.caption("Counterfactual Safety-Aware Zero-Touch Network Simulation")

# Use session state so the network persists when Streamlit reruns.
if "network" not in st.session_state:
    st.session_state.network = NetworkModel()

network = st.session_state.network
safety = SafetyField()
controller = NetworkController(network)

st.subheader("Network Status")

rows = []
for name, link in network.links.items():
    usage = network.utilization(name)
    rows.append({
        "Link": name,
        "Traffic (Mbps)": round(link["traffic"], 2),
        "Capacity (Mbps)": link["capacity"],
        "Utilization (%)": round(usage, 2),
        "Status": safety.status(usage),
        "Delay (ms)": link.get("delay", 0),
        "Packet loss (%)": link.get("packet_loss", 0),
    })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)

col1, col2, col3 = st.columns(3)
col1.metric("Peak utilization", f"{network.peak_utilization():.1f}%")
col2.metric("Average utilization", f"{network.average_utilization():.1f}%")
col3.metric("Congested links", len(network.congested_links()))

st.subheader("Link Utilization")
fig, ax = plt.subplots()
ax.bar(df["Link"], df["Utilization (%)"])
ax.axhline(80, linestyle="--", label="Safety limit (80%)")
ax.set_ylabel("Utilization (%)")
ax.legend()
st.pyplot(fig)
plt.close(fig)

st.subheader("Counterfactual Analysis")
congested = network.congested_links()

if congested:
    source = max(congested, key=network.utilization)
    candidates = controller.preview_actions(source)

    if candidates:
        action_df = pd.DataFrame([
            {
                "Source": item["source"],
                "Destination": item["destination"],
                "Traffic moved (Mbps)": item["amount"],
                "Projected peak (%)": round(item["peak"], 2),
                "Risk score": round(item["risk"], 3),
            }
            for item in candidates
        ]).sort_values("Projected peak (%)")

        st.dataframe(action_df, use_container_width=True, hide_index=True)

        if st.button("Execute safest action"):
            success = controller.control_network()
            if success:
                st.success("Safe transfer applied to the simulated network.")
                st.rerun()
            else:
                st.warning("No safe action could be applied.")
    else:
        st.warning("No safe transfer options are available.")
else:
    st.success("All links are below the safety limit.")

if st.button("Reset network to initial state"):
    st.session_state.network = NetworkModel()
    st.rerun()