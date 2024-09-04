from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import get_args

import typer
from rich import print
from rich.prompt import FloatPrompt, Prompt

from chimer.magnitude_store import (
    GFInterpolation,
    PeakAmplitudesBase,
    PeakAmplitudesStore,
    PeakAmplitudeStoreCache,
)
from chimer.utils import DEFAULT_CACHE_DIR, MeasurementUnit, Range

KM = 1e3

app = typer.Typer(
    name="chimer",
    help="A command line interface for managing PGM stores.",
)

logging.basicConfig(level=logging.DEBUG)


def get_cache(cache_dir: Path = DEFAULT_CACHE_DIR) -> PeakAmplitudeStoreCache:
    return PeakAmplitudeStoreCache(cache_dir=cache_dir)


@app.command()
def list() -> None:
    """List cached PGM stores."""
    store_cache = get_cache()
    print(store_cache.get_all_cached_stores())
    for store in store_cache.get_all_cached_stores():
        ...
        # print(store)


@app.command()
def create(store_id: str, gf_dir: Path = Path.cwd()) -> None:
    """Create a new PGM store from a Pyrocko GF database."""
    from pyrocko.gf import LocalEngine

    engine = LocalEngine(use_config=True, store_superdirs=[str(gf_dir)])
    engine.get_store_ids()
    if store_id not in engine.get_store_ids():
        raise ValueError(f"Store {store_id} not found in {gf_dir}")

    store = engine.get_store(store_id)

    print(f"Creating a new PGM store for Pyrocko GF Store: {store_id}")
    quantity = Prompt.ask(
        "Enter the quantity",
        default=get_args(MeasurementUnit)[0],
        choices=get_args(MeasurementUnit),
    )
    frequency_min = FloatPrompt.ask(
        "Enter the minimum frequency",
        default=0.0,
    )
    while True:
        frequency_max = FloatPrompt.ask(
            "Enter the maximum frequency",
            default=1.0 / store.config.deltat,
        )
        if frequency_min < frequency_max:
            break
        print("[red]Maximum frequency must be greater than minimum frequency")

    reference_magnitude = FloatPrompt.ask(
        "Enter the reference magnitude",
        default=1.0,
    )
    rupture_velocities_min = FloatPrompt.ask(
        "Minimum rupture velocity (x Vs)",
        default=0.8,
    )
    rupture_velocities_max = FloatPrompt.ask(
        "Maximum rupture velocity (x Vs)",
        default=0.9,
    )
    gf_interpolation: str = Prompt.ask(
        "Enter the interpolation method",
        default=get_args(GFInterpolation)[0],
        choices=get_args(GFInterpolation),
    )
    config = PeakAmplitudesBase(
        gf_store_id=store_id,
        quantity=quantity,
        frequency_range=Range(frequency_min, frequency_max),
        rupture_velocities=Range(rupture_velocities_min, rupture_velocities_max),
        reference_magnitude=reference_magnitude,
        source_depth_delta=store.config.source_depth_delta,
        max_distance=store.config.distance_max,
        gf_interpolation=gf_interpolation,
    )

    PeakAmplitudesStore.set_engine(engine)
    PeakAmplitudesStore.set_cache_dir(DEFAULT_CACHE_DIR)

    amp_store = PeakAmplitudesStore.from_selector(config)
    asyncio.run(amp_store.fill_source_depth_range())
    amp_store.save()


@app.command()
def delete(store_id: str) -> None:
    """Delete an existing PGM store from cache."""
    store_cache = get_cache()
    store_cache.clear_cache()


@app.command()
def serve() -> None:
    """Serve PGM stores on a REST API."""
    print("Hello")


def main():
    app()
