# Vmax-F1 Strategy Lab

A small, editable local Streamlit app for exploring how pit timing and tire-wear assumptions change a modeled race time. This is a teaching simulator, not an accurate real-world F1 prediction. It uses no official F1 branding, assets, or claimed real data.

## Run it on a Mac

1. Install Python 3.9.6 if it is not already available. In Terminal, check with `python3 --version`.
2. Unzip the downloaded project and move into its folder:

   ```sh
   cd ~/Downloads/vmax-f1-mvp
   ```

   If you extracted it elsewhere, use that folder's path instead.
3. Create an isolated environment and activate it:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install the app's dependencies:

   ```sh
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Start the app:

   ```sh
   streamlit run app.py
   ```

   Your browser should open the local app. Stop it with Control-C in Terminal. Next time, reopen Terminal, return to the project folder, run `source .venv/bin/activate`, then `streamlit run app.py`.

### One-click launch after the first installation

Once the setup above has completed, you can open the project folder in Finder and double-click `start.command`. A Terminal window will stay open while the simulator runs. To stop it, click that window and press Control-C. If macOS asks whether to open the file, choose Open.

## What you can change

- Race length, baseline lap time, and fixed pit-stop time loss.
- Illustrative Soft, Medium, and Hard tire degradation assumptions.
- Two one-stop strategies: pit lap and the tire used for each stint.
- Lap-to-lap random variation, number of Monte Carlo runs, and a random seed.

The result table shows no-noise modeled time plus Monte Carlo average, median, and 10th–90th percentile. The chart shows the simulated time distributions.

## Model in plain language

For each lap, the program adds baseline time and tire-age wear:

`lap time = baseline lap time + tire age × compound degradation`

At the end of a chosen pit lap, it adds the fixed pit loss, switches to the second stint's compound, and resets tire age to zero. Each Monte Carlo run adds independent normally distributed random variation to each lap. This deliberately omits weather, safety cars, traffic, mechanical failures, fuel effects, and opponent behavior.

## Project files

- `app.py` — controls, result table, and chart.
- `simulator.py` — race calculation and Monte Carlo sampling.
- `tests/test_simulator.py` — small checks of the calculation.
- `requirements.txt` — packages needed by the app.

To run the core checks from the project folder, with the environment activated, use `python -m unittest discover -s tests`.
