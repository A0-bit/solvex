"""
Utility functions for the reports app.
"""
from __future__ import annotations

import io

from PIL import Image


# ---------------------------------------------------------------------------
# Area resolver
# ---------------------------------------------------------------------------

def resolve_area(lat: float, lng: float):
    """
    Given coordinates, return the Area whose boundary polygon contains the
    point, or None if no area matches.

    Boundary is stored as [[lat, lng], ...]; Shapely expects (x=lng, y=lat).
    """
    try:
        from shapely.geometry import Point, Polygon
        from areas.models import Area
    except ImportError:
        return None

    point = Point(float(lng), float(lat))

    for area in Area.objects.exclude(boundary=[]):
        try:
            # Convert [[lat, lng], ...] → [(lng, lat), ...] for Shapely
            coords = [(p[1], p[0]) for p in area.boundary]
            if len(coords) < 3:
                continue
            polygon = Polygon(coords)
            if polygon.is_valid and polygon.contains(point):
                return area
        except Exception:
            continue

    return None


# ---------------------------------------------------------------------------
# EXIF stripping
# ---------------------------------------------------------------------------

def strip_exif(image_file) -> bytes:
    """
    Return image bytes with all EXIF/metadata stripped.
    Protects reporter privacy by removing GPS tags and other metadata.
    """
    img = Image.open(image_file)
    fmt = img.format or "JPEG"

    # Convert RGBA → RGB for JPEG compatibility
    if fmt == "JPEG" and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    data = list(img.getdata())
    clean_img = Image.new(img.mode, img.size)
    clean_img.putdata(data)

    buf = io.BytesIO()
    clean_img.save(buf, format=fmt)
    buf.seek(0)
    return buf.getvalue()
