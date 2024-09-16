# Chimer

*Earthquake Moment Magnitude Estimation from Peak Ground Motion*

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)

*Chimer* is a framework for earthquake moment magnitude estimation from observed peak ground motions (PGM). It builds on top of `pyrocko.gf` Green's function data bases for forward modelling seismic sources and waveforms.

Key features include:

* Creation of synthetic ground motion databases
* Caluclation of statistical peak acceleration, velocity and displacement
* Forward modelling of PGM

## Example

```python
from chimer.magnitude_store import PeakAmplitudesBase, PeakAmplitudesStore

from pyrocko import gf

KM = 1e3

engine = gf.LocalEngine(use_config=True)

peak_amplitudes = PeakAmplitudesBase(
        gf_store_id=store_id,
        quantity="displacement",
    )

PeakAmplitudesStore.set_engine(engine)
store = PeakAmplitudesStore.from_selector(peak_amplitudes)

await store.compute_site_amplitudes(source_depth=2 * KM, reference_magnitude=1.0)
await store.find_moment_magnitude(
    source_depth=2 * KM,
    distance=10 * KM,
    observed_amplitude=0.0001,
)
```

## Installation

Simple installation from GitHub.

```sh
pip install git+https://github.com/pyrocko/chimer
```

## Citation

Please cite chimer as:

> Torsten Dahm, Daniela Kühn, Simone Cesca, Marius Paul Isken, Sebastian Heimann, Earthquake Moment Magnitudes from Peak Ground Displacements and Synthetic Green's Functions, Seismica, 2024, *submitted*

## License

Contribution and merge requests by the community are welcome!

Qseek was written by Marius Paul Isken and is licensed under the GNU GENERAL PUBLIC LICENSE v3.
