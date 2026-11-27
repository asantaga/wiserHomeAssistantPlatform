"""Prepare shared, content-addressed Wiser device artwork from catalogue originals.

Requires Pillow when preparing images. Existing published image files are retained
so independently released cards can continue using their previous URLs.
"""

import argparse
from collections import deque
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

IMAGES = Path(__file__).resolve().parents[1] / "custom_components/wiser/frontend/images"

SOURCE_FILES = {
    "controller": "hub.png", "temperature-humidity": "sensor.png",
    "radiator-thermostat": "trv.png", "room-thermostat": "roomstat-edit.png",
    "smart-plug": "plug-edit.png", "underfloor-heating": "ufh-edit.png",
    "heating-actuator": "actuator-edit.png", "dimmer": "dimmer.png",
    "power": "power.png", "shutter": "shutter.png", "smoke": "smoke.png",
    "leak": "leak.png", "motion": "motion.png", "window": "window.png",
    "cfmt": "cfmt.jpg", "powertag": "powertag.jpg",
    "button": "button.jpg", "boiler": "boiler.jpg",
}

def cutout(image):
    """Remove border-connected white only when the source has no alpha cutout."""
    image = image.convert("RGBA")
    if image.getchannel("A").getextrema()[0] < 255:
        return image
    width, height = image.size
    pixels = image.load()
    visited = set()
    queue = deque([(x, y) for x in range(width) for y in (0, height-1)] +
                  [(x, y) for y in range(height) for x in (0, width-1)])
    while queue:
        x, y = queue.popleft()
        if (x, y) in visited or not (0 <= x < width and 0 <= y < height):
            continue
        visited.add((x, y))
        r, g, b, a = pixels[x, y]
        if min(r, g, b) < 245 or max(r, g, b) - min(r, g, b) > 10:
            continue
        pixels[x, y] = (r, g, b, 0)
        queue.extend(((x-1,y), (x+1,y), (x,y-1), (x,y+1)))
    return image


def write_catalogue(output, sources, images):
    """Write shared PNGs and both catalogues, retaining previously published files."""
    urls = {}
    files = {}
    for model, entry in sources.items():
        data = images[entry["file"]]
        digest = sha256(data).hexdigest()[:12]
        filename = f"{Path(entry['file']).stem}-{digest}.png"
        files[filename] = data
        urls[model] = f"/wiser/images/devices/{filename}"
    (output / "devices").mkdir(parents=True, exist_ok=True)
    for filename, data in files.items():
        (output / "devices" / filename).write_bytes(data)
    for filename, catalogue in (("manifest.json", urls), ("SOURCES.json", sources)):
        (output / filename).write_text(json.dumps(catalogue, indent=2) + "\n", encoding="utf-8")
    return urls


def prepare_images(source, output):
    """Prepare all source images on transparent 640px canvases and update URLs."""
    from PIL import Image

    sources = json.loads((IMAGES / "SOURCES.json").read_text(encoding="utf-8"))
    images = {}
    for filename in dict.fromkeys(entry["file"] for entry in sources.values()):
        name = Path(filename).stem
        with Image.open(source / SOURCE_FILES[name]) as original:
            image = cutout(original)
        bounds = image.getchannel("A").getbbox()
        if bounds is None:
            raise ValueError(f"Empty product artwork: {name}")
        image = image.crop(bounds)
        image.thumbnail((560, 560), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (640, 640))
        canvas.alpha_composite(image, ((640-image.width)//2, (640-image.height)//2))
        if canvas.getchannel("A").getextrema() != (0, 255):
            raise ValueError(f"Expected transparent surroundings and opaque product: {name}")
        buffer = BytesIO()
        canvas.save(buffer, format="PNG", optimize=True)
        images[filename] = buffer.getvalue()
    # Process every source successfully before changing any catalogue or asset.
    urls = write_catalogue(output, sources, images)
    print(f"Prepared {len(images)} shared images for {len(urls)} device types in {output}")


def main():
    """Read original catalogue artwork from a directory supplied by the maintainer."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Directory of catalogue originals named in SOURCE_FILES")
    parser.add_argument("--output", type=Path, default=IMAGES, help="Shared image directory (default: integration frontend/images)")
    args = parser.parse_args()
    prepare_images(args.source, args.output)


if __name__ == "__main__":
    main()
