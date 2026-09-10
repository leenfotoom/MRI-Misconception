from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesResult:
    voltage: float
    resistances: list[float]
    total_resistance: float
    current: float
    voltage_drops: list[float]
    powers: list[float]


@dataclass(frozen=True)
class ParallelResult:
    voltage: float
    resistances: list[float]
    equivalent_resistance: float
    branch_currents: list[float]
    total_current: float
    branch_powers: list[float]


def solve_series(voltage: float, resistances: list[float]) -> SeriesResult:
    if voltage <= 0:
        raise ValueError("Voltage must be positive")
    if not resistances or any(r <= 0 for r in resistances):
        raise ValueError("All resistances must be positive")
    total = sum(resistances)
    current = voltage / total
    drops = [current * r for r in resistances]
    powers = [(current ** 2) * r for r in resistances]
    return SeriesResult(voltage, resistances, total, current, drops, powers)


def solve_parallel(voltage: float, resistances: list[float]) -> ParallelResult:
    if voltage <= 0:
        raise ValueError("Voltage must be positive")
    if not resistances or any(r <= 0 for r in resistances):
        raise ValueError("All resistances must be positive")
    inv = sum(1.0 / r for r in resistances)
    req = 1.0 / inv
    currents = [voltage / r for r in resistances]
    total_current = sum(currents)
    powers = [(voltage ** 2) / r for r in resistances]
    return ParallelResult(voltage, resistances, req, currents, total_current, powers)
