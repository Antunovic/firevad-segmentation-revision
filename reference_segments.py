"""Read-only comparison of the two original annotation sets."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Optional


TOLERANCE = 10
ANNOTATORS = (
    ("Antonio", "Antonio", ("#85b8df", "#bddcf3"), "#20577e"),
    ("Mislav", "Mislav_Caleta", ("#f5ab63", "#f9d2ac"), "#8d440a"),
)


@dataclass(frozen=True)
class Reference:
    segments: tuple

    @property
    def frame_count(self):
        return self.segments[-1][1] + 1

    @property
    def boundaries(self):
        return tuple(start for start, _ in self.segments[1:])


@dataclass(frozen=True)
class Comparison:
    antonio: Optional[Reference]
    mislav: Optional[Reference]
    issues: tuple

    @property
    def needs_revision(self):
        return bool(self.issues)

    @property
    def status(self):
        if self.issues:
            return "Review: " + "; ".join(self.issues)
        if not self.antonio or not self.mislav:
            return "Reference missing" if self.antonio or self.mislav else "No references"
        return f"Agrees (±{TOLERANCE} frames)"


def compare(antonio, mislav, rgb_count=None, ir_count=None):
    issues = []
    if antonio and mislav:
        if antonio.frame_count != mislav.frame_count:
            issues.append("Reference frame counts differ")
        if len(antonio.segments) != len(mislav.segments):
            issues.append("Segment counts differ")
        # For equally sized, sorted lists, an in-tolerance perfect matching
        # exists exactly when pairing the boundaries in order succeeds.
        elif any(abs(a - b) > TOLERANCE for a, b in zip(antonio.boundaries, mislav.boundaries)):
            issues.append(f"Boundary offset >{TOLERANCE} frames")
    if rgb_count is not None and ir_count is not None:
        if rgb_count != ir_count:
            issues.append("RGB/IR frame counts differ")
        if any(ref.frame_count not in (rgb_count, ir_count) for ref in (antonio, mislav) if ref):
            issues.append("Dataset length differs from reference")
    return Comparison(antonio, mislav, tuple(issues))


def _read_reference(path, env, scene):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if (data["environment"], data["video_id"]) != (env, scene):
            raise ValueError("scene ID does not match its filename")
        segments = tuple((seg["start_frame"], seg["end_frame"]) for seg in data["segments"])
        if not segments:
            raise ValueError("no segments")
        next_start = 0
        for start, end in segments:
            if type(start) is not int or type(end) is not int or start != next_start or end < start:
                raise ValueError("segments must be consecutive and start at frame 0")
            next_start = end + 1
        return Reference(segments)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid reference annotation {path}: {exc}") from exc


class ReferenceAnnotations:
    def __init__(self, root):
        self.by_annotator = []
        for _, folder, _, _ in ANNOTATORS:
            scenes = {}
            for path in sorted((Path(root) / folder).glob("environment_*/*.json")):
                env_id = re.fullmatch(r"environment_(\d+)", path.parent.name)
                if not env_id or not path.stem.isdecimal():
                    continue
                key = (int(env_id[1]), int(path.stem))
                if key in scenes:
                    raise ValueError(f"Duplicate reference annotation: {path}")
                scenes[key] = _read_reference(path, *key)
            self.by_annotator.append(scenes)

    def for_scene(self, env, scene, rgb_count=None, ir_count=None):
        antonio, mislav = (scenes.get((env, scene)) for scenes in self.by_annotator)
        return compare(antonio, mislav, rgb_count, ir_count)
