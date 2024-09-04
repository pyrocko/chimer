from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal, NamedTuple

import numpy as np
from pydantic import AfterValidator, ByteSize
from pyrocko.trace import Trace

logger = logging.getLogger(__name__)

MeasurementUnit = Literal[
    "displacement",
    "velocity",
    "acceleration",
]

DEFAULT_CACHE_DIR = Path("~/.cache/chimer").expanduser()
if not DEFAULT_CACHE_DIR.exists():
    logger.info("Creating cache directory %s", DEFAULT_CACHE_DIR)
    DEFAULT_CACHE_DIR.mkdir(parents=True)


@dataclass
class ChannelSelector:
    channels: str
    number_channels: int
    normalize: bool = False

    def get_traces(self, traces_flt: list[Trace]) -> list[Trace]:
        """Filter and normalize a list of traces based on the specified channels.

        Args:
            traces_flt (list[Trace]): The list of traces to filter.

        Returns:
            list[Trace]: The filtered and normalized list of traces.

        Raises:
            KeyError: If the number of channels in the filtered list does not match
                the expected number of channels.
        """
        nsls = {tr.nslc_id[:3] for tr in traces_flt}
        if len(nsls) != 1:
            raise KeyError(
                f"cannot get traces for selector {self.channels}"
                f" available: {', '.join('.'.join(tr.nslc_id) for tr in traces_flt)}"
            )

        traces_flt = [tr for tr in traces_flt if tr.channel[-1] in self.channels]

        tmins = {tr.tmin for tr in traces_flt}
        tmaxs = {tr.tmax for tr in traces_flt}
        if len(tmins) != 1 or len(tmaxs) != 1:
            raise KeyError(
                f"unhealthy timing on channels {self.channels}",
                f" for: {', '.join('.'.join(tr.nslc_id) for tr in traces_flt)}",
            )

        if len(traces_flt) != self.number_channels:
            raise KeyError(
                f"cannot get {self.number_channels} channels"
                f" for selector {self.channels}"
                f" available: {', '.join('.'.join(tr.nslc_id) for tr in traces_flt)}"
            )
        if self.normalize:
            traces_norm = traces_flt[0].copy()
            data = np.atleast_2d(np.array([tr.ydata for tr in traces_flt]))

            traces_norm.ydata = np.linalg.norm(data, axis=0)
            return [traces_norm]
        return traces_flt

    __call__ = get_traces


class ChannelSelectors:
    All = ChannelSelector("ENZ0123RT", 3)
    HorizontalAbs = ChannelSelector("EN123RT", 2, normalize=True)
    Horizontal = ChannelSelector("EN123RT", 2)
    Vertical = ChannelSelector("Z0", 1)
    NorthEast = ChannelSelector("NE", 2)


class _Range(NamedTuple):
    min: float
    max: float

    def inside(self, value: float) -> bool:
        """Check if a value is inside the range.

        Args:
            value (float): The value to check.

        Returns:
            bool: True if the value is inside the range, False otherwise.
        """
        return self.min <= value <= self.max

    @classmethod
    def from_list(cls, array: np.ndarray | list[float]) -> _Range:
        """Create a Range object from a numpy array.

        Parameters:
        - array: numpy.ndarray
            The array from which to create the Range object.

        Returns:
        - _Range: The created Range object.
        """
        return cls(min=np.min(array), max=np.max(array))


def _range_validator(v: _Range) -> _Range:
    if v.min > v.max:
        raise ValueError(f"Bad range {v}, must be (min, max)")
    return v


Range = Annotated[_Range, AfterValidator(_range_validator)]


def human_readable_bytes(size: int | float, decimal: bool = False) -> str:
    """Convert a size in bytes to a human-readable string representation.

    Args:
        size (int | float): The size in bytes.
        decimal: If True, use decimal units (e.g. 1000 bytes per KB).
            If False, use binary units (e.g. 1024 bytes per KiB).

    Returns:
        str: The human-readable string representation of the size.

    """
    return ByteSize(size).human_readable(decimal=decimal)
