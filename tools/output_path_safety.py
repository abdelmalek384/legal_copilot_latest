"""Fail-closed guards for CLI report paths that must not replace evidence inputs."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


def _same_file_or_path(left: Path, right: Path) -> bool:
    """Detect lexical/resolved path equality and existing hard-link aliases."""
    try:
        if left.resolve(strict=False) == right.resolve(strict=False):
            return True
        if left.exists() and right.exists():
            return left.samefile(right)
    except (OSError, RuntimeError) as exc:
        raise ValueError(
            f"cannot safely compare report path {left} with protected path {right}: {exc}"
        ) from exc
    return False


def ensure_output_paths_safe(
    output_paths: Iterable[Path],
    protected_input_paths: Iterable[Path],
) -> None:
    """Reject report paths that alias protected inputs or another report output.

    Resolving paths catches relative-path and symlink aliases. samefile also
    catches existing hard links. This check runs before output files are opened.
    """
    outputs = [Path(path) for path in output_paths if path is not None]
    inputs = [Path(path) for path in protected_input_paths if path is not None]

    for index, output in enumerate(outputs):
        for protected in inputs:
            if _same_file_or_path(output, protected):
                raise ValueError(
                    f"refusing to write report to {output}: it aliases protected input {protected}"
                )
        for other in outputs[index + 1:]:
            if _same_file_or_path(output, other):
                raise ValueError(
                    f"report output paths must be distinct: {output} aliases {other}"
                )
