"""Transparent, F1-inspired race strategy model for learning purposes."""

from dataclasses import dataclass
import random
from typing import Dict, List, Optional, Sequence


@dataclass
class Strategy:
    name: str
    pit_laps: List[int]
    compounds: List[str]


def simulate_race(
    race_laps: int,
    base_lap_seconds: float,
    pit_loss_seconds: float,
    degradation: Dict[str, float],
    strategy: Strategy,
    lap_noise_std: float = 0.0,
    rng: Optional[random.Random] = None,
) -> float:
    """Simulate one race; pit_laps are the laps completed before stopping.

    Every pit stop changes to the next compound listed in ``strategy.compounds``.
    Tire age resets after a stop. Lap noise is independent normal noise.
    """
    if race_laps < 1:
        raise ValueError("race_laps must be at least 1")
    if len(strategy.compounds) != len(strategy.pit_laps) + 1:
        raise ValueError("Provide one compound for each stint")
    if strategy.pit_laps != sorted(strategy.pit_laps):
        raise ValueError("pit_laps must be in ascending order")
    if any(lap < 1 or lap >= race_laps for lap in strategy.pit_laps):
        raise ValueError("Pit laps must be between lap 1 and the final lap - 1")
    if len(set(strategy.pit_laps)) != len(strategy.pit_laps):
        raise ValueError("Pit laps must be unique")
    for compound in strategy.compounds:
        if compound not in degradation:
            raise ValueError("Missing degradation value for " + compound)

    rng = rng or random.Random()
    pit_set = set(strategy.pit_laps)
    stint_index = 0
    tire_age = 0
    total = 0.0
    for lap in range(1, race_laps + 1):
        compound = strategy.compounds[stint_index]
        total += base_lap_seconds + tire_age * degradation[compound]
        if lap_noise_std > 0:
            total += rng.gauss(0.0, lap_noise_std)
        if lap in pit_set:
            total += pit_loss_seconds
            stint_index += 1
            tire_age = 0
        else:
            tire_age += 1
    return total


def monte_carlo(
    race_laps: int,
    base_lap_seconds: float,
    pit_loss_seconds: float,
    degradation: Dict[str, float],
    strategy: Strategy,
    trials: int = 1000,
    lap_noise_std: float = 0.5,
    seed: Optional[int] = None,
) -> List[float]:
    """Return simulated totals with a reproducible seed when supplied."""
    if trials < 1:
        raise ValueError("trials must be at least 1")
    rng = random.Random(seed)
    return [
        simulate_race(race_laps, base_lap_seconds, pit_loss_seconds,
                      degradation, strategy, lap_noise_std, rng)
        for _ in range(trials)
    ]


def summarize(values: Sequence[float]) -> Dict[str, float]:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("values must not be empty")
    n = len(ordered)
    return {
        "mean": sum(ordered) / n,
        "p10": ordered[int((n - 1) * 0.10)],
        "median": ordered[int((n - 1) * 0.50)],
        "p90": ordered[int((n - 1) * 0.90)],
    }
