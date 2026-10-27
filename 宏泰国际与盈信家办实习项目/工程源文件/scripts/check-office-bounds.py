#!/usr/bin/env python3
"""Check normalized browser DOM bounds captured by ScenesV12Offices.

Usage: python3 check-office-bounds.py <audit.json> <output.json>
An input filename containing "stills" permits partial coverage. Other filenames
require all 2,103 frames, including all 293 frames of the changed section.
This checks DOM boxes and rectangular masks, not rendered glyph ink or pixels.
"""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

EPS = 0.001
ROOT = dict(x=0, y=0, width=1920, height=1080)
CAPTION = dict(x=105, y=967, width=1710, height=55)
TEXT = dict(x=130, y=300, width=430, height=600)
PHOTO = dict(x=640, y=300, width=1150, height=600)
START, TRUST, END, TOTAL = 1359, 1569, 1652, 2103
EYES, FAITH = "眼光，跨越地域。", "信任，扎根時間。"


def rectangle(value):
    if not isinstance(value, dict):
        raise ValueError("missing rectangle")
    result = {k: float(value[k]) for k in ("x", "y", "width", "height")}
    if not all(math.isfinite(v) for v in result.values()):
        raise ValueError("non-finite rectangle")
    if result["width"] < 0 or result["height"] < 0:
        raise ValueError("negative rectangle dimensions")
    return result


def right(r):
    return r["x"] + r["width"]


def bottom(r):
    return r["y"] + r["height"]


def intersection(*rects):
    x, y = max(r["x"] for r in rects), max(r["y"] for r in rects)
    w, h = min(right(r) for r in rects) - x, min(bottom(r) for r in rects) - y
    return dict(x=x, y=y, width=w, height=h) if w > EPS and h > EPS else None


def contains(outer, inner):
    return (inner["x"] >= outer["x"] - EPS and inner["y"] >= outer["y"] - EPS
            and right(inner) <= right(outer) + EPS
            and bottom(inner) <= bottom(outer) + EPS)


def same_rect(a, b):
    return all(abs(a[k] - b[k]) <= EPS for k in b)


def inset_rect(css, tile):
    """Resolve CSS inset() shorthand; percentages use the matching box axis."""
    if css == "none":
        return dict(tile)
    match = re.fullmatch(r"inset\(([^()]*)\)", css.strip())
    if not match:
        raise ValueError(f"unsupported clip-path: {css}")
    parts = match.group(1).split()
    if not 1 <= len(parts) <= 4:
        raise ValueError(f"unsupported inset shorthand: {css}")
    parts = {1: lambda p: p * 4, 2: lambda p: p * 2,
             3: lambda p: [p[0], p[1], p[2], p[1]], 4: lambda p: p}[len(parts)](parts)
    lengths = []
    for i, token in enumerate(parts):
        m = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)(%|px)?", token, re.I)
        if not m or (not m.group(2) and float(m.group(1)) != 0):
            raise ValueError(f"unsupported inset length: {token}")
        v = float(m.group(1))
        if m.group(2) == "%":
            v *= tile["height" if i % 2 == 0 else "width"] / 100
        lengths.append(v)
    top, r, b, left = lengths
    width, height = tile["width"] - left - r, tile["height"] - top - b
    # Insets that consume a whole axis have no positive-area visible region.
    if width <= EPS or height <= EPS:
        return None
    return dict(x=tile["x"] + left, y=tile["y"] + top, width=width, height=height)


def main(source, output):
    raw = source.read_bytes()
    data = json.loads(raw)
    records = list(data.values()) if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise ValueError("audit must be a frame-keyed object or a list")
    rows, failures, minimums, details = {}, [], {}, []
    checks = 0

    def check(condition, frame, rule, evidence=None):
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(dict(frame=frame, rule=rule, evidence=evidence))

    def gap(label, value):
        minimums[label] = min(minimums.get(label, value), value)

    for record in records:
        frame = record.get("frame") if isinstance(record, dict) else None
        if not isinstance(frame, int) or isinstance(frame, bool):
            check(False, frame, "integer frame field")
            continue
        check(frame not in rows, frame, "unique frame record")
        rows[frame] = record
        check(0 <= frame < TOTAL, frame, "frame within 0..2102")

    is_stills = "stills" in source.name.lower()
    expected_active = set(range(START, END))
    sampled_active = expected_active.intersection(rows)
    all_frames = set(range(TOTAL))
    full_coverage = set(rows) == all_frames
    active_coverage = sampled_active == expected_active
    if not is_stills:
        check(full_coverage, None, "full audit covers all 2103 frames",
              sorted(all_frames.difference(rows)))
        check(active_coverage, None, "full audit covers all 293 active frames",
              sorted(expected_active.difference(rows)))
    check(bool(rows), None, "audit contains frame records")

    for frame, row in sorted(rows.items()):
        try:
            root, cap = rectangle(row.get("rootRect")), rectangle(row.get("captionRect"))
            check(abs(root["width"] - 1920) <= EPS and abs(root["height"] - 1080) <= EPS,
                  frame, "rendered root measures 1920x1080", root)
            check(same_rect(cap, CAPTION), frame, "normalized caption rectangle unchanged", cap)
            active = START <= frame < END
            check(row.get("active") is active, frame, "active section flag agrees with frame range")
            # Title checks use the exact main-title strings. Narration subtitles
            # have different wording and do not count as a second main title.
            text = row.get("text", "")
            check(not (EYES in text and FAITH in text), frame, "two main headlines never share DOM")
            if not active:
                continue
            trust = frame >= TRUST
            check(row.get("trust") is trust, frame, "office/trust page range agrees with frame")
            info = dict(frame=frame, page="trust" if trust else "office", effective_tiles=[])
            details.append(info)
            if trust:
                check(row.get("headline") is None and row.get("trustHeadline") is not None,
                      frame, "independent trust headline only")
                check(FAITH in text and EYES not in text, frame, "trust title text is exclusive")
                check(not row.get("tiles") and row.get("photoRegion") is None,
                      frame, "trust page has no remaining office photographs")
                legal = row.get("legal")
                check(isinstance(legal, dict), frame, "trust page contains integrated lower-left legal block")
                if isinstance(legal, dict):
                    r = rectangle(legal.get("rect"))
                    opacity = float(legal["opacity"])
                    check(contains(ROOT, r) and r["x"] <= 130 and r["y"] >= bottom(cap),
                          frame, "legal block is inside lower left beneath subtitle", r)
                    check(intersection(r, cap) is None, frame, "legal does not intersect subtitle")
                    check(legal.get("fontSize") == "14px", frame, "legal font size is 14px")
                    check(0 <= opacity <= .28 + EPS, frame, "legal opacity remains <= 0.28", opacity)
                    gap("caption_to_legal_vertical_px", r["y"] - bottom(cap))
                    gap("legal_to_canvas_bottom_px", 1080 - bottom(r))
                    info["legal"] = dict(rect=r, opacity=opacity, font_size=legal.get("fontSize"))
                continue

            region, photo, name_clip = (rectangle(row.get(k)) for k in ("textRegion", "photoRegion", "nameClip"))
            check(same_rect(region, TEXT), frame, "left text region matches specified rectangle", region)
            check(same_rect(photo, PHOTO), frame, "right photo region matches specified rectangle", photo)
            check(intersection(region, photo) is None, frame, "text and photo regions do not intersect")
            check(row.get("headline") is not None and row.get("trustHeadline") is None,
                  frame, "office headline only")
            check((EYES in text) == (frame >= 1493) and FAITH not in text,
                  frame, "vision page starts with New York, no trust main title")
            check(row.get("legal") is None, frame, "detailed legal stays on trust page")
            check(contains(region, name_clip), frame, "city-name clipping box stays inside text region")
            gap("text_to_photo_horizontal_px", photo["x"] - right(region))
            gap("photo_to_caption_vertical_px", cap["y"] - bottom(photo))
            blocks = row.get("textBlocks", [])
            for block in blocks:
                r, role = rectangle(block.get("rect")), block.get("role")
                if role in ("current", "outgoing"):
                    # Both names intentionally share a clipping frame while
                    # fading. Raw translated boxes can extend beyond that mask.
                    visible_name = intersection(r, name_clip, region)
                    if visible_name:
                        check(contains(region, visible_name), frame, "masked city name stays within text region")
                    continue
                check(contains(region, r), frame, "fixed text block stays inside text region", role)
                check(intersection(name_clip, r) is None, frame,
                      "city-name clipping frame does not overlap other text block", role)
                if bottom(r) <= name_clip["y"] + EPS:
                    gap("name_clip_to_other_text_vertical_px", name_clip["y"] - bottom(r))
                elif r["y"] >= bottom(name_clip) - EPS:
                    gap("name_clip_to_other_text_vertical_px", r["y"] - bottom(name_clip))

            for tile in row.get("tiles", []):
                box, image = rectangle(tile.get("rect")), rectangle(tile.get("rawImage"))
                mask = inset_rect(tile.get("clip", ""), box)
                effective = intersection(box, image, mask) if mask else None
                check(contains(photo, box), frame, "tile frame is contained by photo region", tile.get("id"))
                check(contains(image, box), frame, "transformed image covers its tile frame", tile.get("id"))
                check(bool(tile.get("visible")) == bool(effective), frame,
                      "reported tile visibility agrees with resolved mask", tile.get("id"))
                if effective:
                    check(contains(photo, effective), frame, "effective masked photo stays inside photo region", tile.get("id"))
                    check(intersection(effective, region) is None, frame, "effective photo does not intersect text region", tile.get("id"))
                    check(intersection(effective, cap) is None, frame, "effective photo does not intersect subtitle", tile.get("id"))
                info["effective_tiles"].append(dict(id=tile.get("id"), clip=tile.get("clip"),
                                                     raw_image=image, tile_frame=box,
                                                     resolved_mask=mask, effective_rect=effective))
        except (ValueError, TypeError, KeyError) as exc:
            check(False, frame, "valid browser bounds audit record", str(exc))

    result = dict(
        passed=not failures, source=str(source.resolve()),
        source_sha256=hashlib.sha256(raw).hexdigest(),
        measurement_basis="Real browser DOM rectangles normalized relative to the 1920x1080 composition root; no glyph-ink claim.",
        mask_method="Resolve CSS inset() percent/px shorthand, then intersect raw transformed image, overflow-hidden tile frame, and mask.",
        name_method="Outgoing/current names may overlap one another inside nameClip; the clipping frame is checked against other text blocks.",
        coverage=dict(mode="stills_partial_allowed" if is_stills else "full_required",
                      total_frames_sampled=len(rows), expected_total_frames=TOTAL,
                      full_coverage=full_coverage, expected_active_frames=END-START,
                      active_frames_sampled=len(sampled_active), full_active_coverage=active_coverage,
                      missing_active_frames=sorted(expected_active-sampled_active)),
        page_ranges=dict(office_inclusive=[START, TRUST-1], trust_inclusive=[TRUST, END-1]),
        expected_static_windows=[dict(city=city, first=f, last=l, frames=l-f+1, seconds=(l-f+1)/30)
                                 for city, f, l in [("Hong Kong",1383,1425),("Shenzhen",1450,1492),("New York",1517,1559)]],
        minimum_gaps_px=minimums, checks=checks, failure_count=len(failures),
        failures=failures[:100], failures_truncated=len(failures)>100,
        active_frame_measurements=details,
        limitations=["Rectangular DOM and mask geometry is measured, not rasterized glyph ink or perceptual legibility.",
                     "Still inputs provide sampled evidence only; full coverage is required for the full-render audit.",
                     "Expected static windows state the timing plan; PNG pixel stationarity is verified separately."],
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("passed","coverage","minimum_gaps_px","checks","failure_count")}, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
