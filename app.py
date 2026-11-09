"""Streamlit interface for the Vmax-F1 learning simulator."""

import statistics

import pandas as pd
import streamlit as st

from simulator import Strategy, monte_carlo, simulate_race, summarize


st.set_page_config(page_title="Vmax-F1 Strategy Lab", page_icon="🏎️", layout="wide")
st.title("🏎️ Vmax-F1 Strategy Lab")
st.caption("A transparent learning model — not a prediction of real F1 results.")

with st.sidebar:
    st.header("Race assumptions")
    race_laps = st.slider("Race laps", 10, 80, 30)
    base_lap = st.number_input("Baseline lap time (seconds)", 30.0, 180.0, 90.0, 0.1)
    pit_loss = st.number_input("Time lost in pit stop (seconds)", 0.0, 60.0, 20.0, 0.5)
    lap_noise = st.number_input("Random lap variation (seconds, std. dev.)", 0.0, 5.0, 0.5, 0.1)
    trials = st.select_slider("Monte Carlo runs", options=[100, 250, 500, 1000, 2500, 5000], value=1000)
    seed = st.number_input("Random seed (repeatable results)", 0, 999999, 42, 1)

st.subheader("Tire assumptions")
st.write("Enter assumed time lost per lap for each tire age. These are illustrative inputs, not measured F1 data.")
comp_cols = st.columns(3)
compound_names = ["Soft", "Medium", "Hard"]
degradation = {}
defaults = [0.12, 0.07, 0.04]
for col, name, default in zip(comp_cols, compound_names, defaults):
    with col:
        degradation[name] = st.number_input(
            name + " degradation (seconds per tire-age lap)", 0.0, 2.0, default, 0.01, key="deg_" + name
        )

st.subheader("Compare two one-stop strategies")
left, right = st.columns(2)
with left:
    st.markdown("#### Strategy A")
    pit_a = st.slider("Pit after lap", 1, race_laps - 1, max(1, race_laps // 3), key="pit_a")
    first_a = st.selectbox("Starting tire", compound_names, index=1, key="first_a")
    second_a = st.selectbox("Tire after stop", compound_names, index=2, key="second_a")
with right:
    st.markdown("#### Strategy B")
    pit_b = st.slider("Pit after lap", 1, race_laps - 1, max(1, 2 * race_laps // 3), key="pit_b")
    first_b = st.selectbox("Starting tire", compound_names, index=0, key="first_b")
    second_b = st.selectbox("Tire after stop", compound_names, index=1, key="second_b")

strategies = [
    Strategy("Strategy A", [pit_a], [first_a, second_a]),
    Strategy("Strategy B", [pit_b], [first_b, second_b]),
]
assumptions = st.expander("Model assumptions", expanded=False)
with assumptions:
    st.markdown("""
- Race pace starts at the same baseline time for every lap.
- Tire wear adds `tire age × selected degradation` to each lap time; tire age resets at a pit stop.
- A stop adds the same fixed pit loss. There are no pit-lane entry effects or traffic interactions.
- Monte Carlo adds independent normally distributed noise to each lap. It models variation, not weather, safety cars, failures, or opponents.
- Each strategy makes exactly one stop. A pit on the selected lap occurs after that lap is completed.
- Results compare only the assumptions entered here; they do not predict real race outcomes.
""")

results = []
distribution = {}
for index, strategy in enumerate(strategies):
    deterministic = simulate_race(race_laps, base_lap, pit_loss, degradation, strategy)
    samples = monte_carlo(race_laps, base_lap, pit_loss, degradation, strategy,
                          trials=trials, lap_noise_std=lap_noise, seed=int(seed) + index)
    stats = summarize(samples)
    results.append({
        "Strategy": strategy.name,
        "Pit lap": strategy.pit_laps[0],
        "Tires": " → ".join(strategy.compounds),
        "No-noise time (s)": deterministic,
        "Average (s)": stats["mean"],
        "Median (s)": stats["median"],
        "10th–90th percentile (s)": "{:.2f}–{:.2f}".format(stats["p10"], stats["p90"]),
    })
    distribution[strategy.name] = samples

st.subheader("Predicted outcomes under this model")
st.dataframe(pd.DataFrame(results).style.format({
    "No-noise time (s)": "{:.2f}", "Average (s)": "{:.2f}", "Median (s)": "{:.2f}"
}), use_container_width=True, hide_index=True)
mean_a = statistics.mean(distribution["Strategy A"])
mean_b = statistics.mean(distribution["Strategy B"])
winner = "A" if mean_a < mean_b else "B" if mean_b < mean_a else None
if winner:
    st.info("Strategy {} has the lower simulated average by {:.2f} seconds in these runs.".format(
        winner, abs(mean_a - mean_b)))
else:
    st.info("The two simulated average times are tied in these runs.")

st.subheader("Monte Carlo results distribution")
hist_rows = []
for strategy_name, samples in distribution.items():
    hist_rows.extend({"Race time (seconds)": value, "Strategy": strategy_name} for value in samples)
hist = pd.DataFrame(hist_rows)
bin_width = max(1.0, round((max(hist["Race time (seconds)"]) - min(hist["Race time (seconds)"])) / 30.0, 1))
hist["Time band (seconds)"] = (hist["Race time (seconds)"] / bin_width).round() * bin_width
counts = hist.groupby(["Time band (seconds)", "Strategy"]).size().unstack(fill_value=0)
st.bar_chart(counts, use_container_width=True)
st.caption("Each run is one simulated race. The plot groups totals into approximate time bands; lower times appear to the left.")
