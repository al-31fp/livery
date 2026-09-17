# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Wingman - feeds the Livery mod your wallpaper and the colours in it.

    uv run wingman.py                 current desktop wallpaper, default Zen profile
    uv run wingman.py photo.jpg       a specific image
    uv run wingman.py --dry-run       print the palette, write nothing
    uv run wingman.py --profile DIR   a specific Zen profile folder

Writes two files into the Zen profile's chrome folder, next to Zen's merged
mods stylesheet, so the mod can @import them by a relative path:

    livery-wallpaper.<ext>   a copy of the image (so the original can move)
    livery-palette.css       :root { --livery-wallpaper: url(...); --livery-accent: ...; }

Then restart Zen, or switch Livery off and on in Settings > Zen Mods.

Needs uv (https://docs.astral.sh/uv/getting-started/installation/), which
fetches Python and Pillow on first run; or any Python 3.10+ with Pillow.
"""
from __future__ import annotations

import argparse
import colorsys
import configparser
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

# --------------------------------------------------------------------------- #
# IMINT - imagery intelligence: which colours the picture is actually made of #
# --------------------------------------------------------------------------- #

SECTORS = 24                       # hue sectors of 15 degrees
SAT_MIN, L_MIN, L_MAX = 0.30, 0.15, 0.85   # what counts as a "colourful" pixel
MAX_SIDE = 256                     # downsample before counting
UI_L_MIN, UI_L_MAX = 0.42, 0.55    # lightness band a UI colour is clamped into
MIN_HUE_GAP = 40                   # degrees between palette entries


def imint(path: Path) -> dict:
    """Pool colourful pixels by hue, score sectors by sqrt(coverage) x vibrancy,
    return accent + up to three palette colours + the dominant colour.

    Hue pooling rather than RGB binning is deliberate: binned at 4 bits per
    channel, a red racing car spread over ~30 tiny bins and lost to a 3-pixel
    speck of orange. Pooled by hue it is the second colour in the image.
    """
    im = Image.open(path).convert("RGB")
    w, h = im.size
    scale = min(1.0, MAX_SIDE / max(w, h))
    im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BOX)
    # get_flattened_data is Pillow >= 11.3; getdata is deprecated for removal in 14.
    pixels = list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())
    total = len(pixels)

    sect = [[0, 0, 0, 0, 0.0] for _ in range(SECTORS)]   # n, r, g, b, sat
    bins: dict[tuple, list] = {}
    for r, g, b in pixels:
        key = (r >> 4, g >> 4, b >> 4)
        d = bins.setdefault(key, [0, 0, 0, 0])
        d[0] += 1; d[1] += r; d[2] += g; d[3] += b
        hue, lum, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if sat < SAT_MIN or not (L_MIN <= lum <= L_MAX):
            continue
        s = sect[int(hue * SECTORS) % SECTORS]
        s[0] += 1; s[1] += r; s[2] += g; s[3] += b; s[4] += sat

    cands = []
    for i, (n, sr, sg, sb, ssat) in enumerate(sect):
        if n == 0:
            continue
        rgb = (sr // n, sg // n, sb // n)
        _, lum, _ = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
        coverage = n / total
        vibrancy = (ssat / n) * (1 - abs(lum - 0.5))
        cands.append((coverage ** 0.5 * vibrancy, i * 360 // SECTORS, rgb, coverage))
    cands.sort(reverse=True)

    picked: list[tuple] = []
    for c in cands:
        if all(min(abs(c[1] - p[1]), 360 - abs(c[1] - p[1])) >= MIN_HUE_GAP for p in picked):
            picked.append(c)
        if len(picked) == 3:
            break

    n, sr, sg, sb = max(bins.values(), key=lambda v: v[0])
    dominant = (sr // n, sg // n, sb // n)
    colours = [_normalise(p[2]) for p in picked]
    return {
        "accent": colours[0] if colours else dominant,
        "palette": colours,
        "dominant": dominant,
        "coverage": picked[0][3] if picked else 0.0,
    }


def _normalise(rgb: tuple) -> tuple:
    """Sector means are pulled dark by shadowed pixels; keep hue and saturation,
    clamp lightness into a band that works as a UI colour."""
    hue, lum, sat = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    lum = min(max(lum, UI_L_MIN), UI_L_MAX)
    return tuple(round(c * 255) for c in colorsys.hls_to_rgb(hue, lum, sat))


def hexs(rgb: tuple) -> str:
    return "#%02x%02x%02x" % rgb


# --------------------------------------------------------------------------- #
# Where things are                                                            #
# --------------------------------------------------------------------------- #

def profiles_ini_candidates() -> list[Path]:
    home = Path.home()
    system = platform.system()
    if system == "Windows":
        import os
        return [Path(os.environ["APPDATA"]) / "zen" / "profiles.ini"]
    if system == "Darwin":
        return [home / "Library" / "Application Support" / "zen" / "profiles.ini"]
    return [
        home / ".zen" / "profiles.ini",
        home / ".var" / "app" / "app.zen_browser.zen" / ".zen" / "profiles.ini",   # flatpak
    ]


def find_profile() -> Path:
    for ini_path in profiles_ini_candidates():
        if not ini_path.exists():
            continue
        ini = configparser.ConfigParser(interpolation=None)
        ini.read(ini_path, encoding="utf-8")
        # The [Install...] section's Default is the profile this installation
        # opens. [ProfileN] Default=1 is an older flag and is not the same thing.
        for section in ini.sections():
            if section.startswith("Install") and ini[section].get("Default"):
                return ini_path.parent / ini[section]["Default"]
        for section in ini.sections():
            if section.startswith("Profile") and ini[section].get("Default") == "1":
                p = ini[section]["Path"]
                return ini_path.parent / p if ini[section].get("IsRelative", "1") == "1" else Path(p)
        for section in ini.sections():
            if section.startswith("Profile"):
                p = ini[section]["Path"]
                return ini_path.parent / p if ini[section].get("IsRelative", "1") == "1" else Path(p)
    sys.exit("Could not find a Zen profile. Open Zen once, or pass --profile <folder> "
             "(about:support > Profile Folder shows it).")


def current_wallpaper() -> Path:
    system = platform.system()
    try:
        if system == "Windows":
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as k:
                p = Path(winreg.QueryValueEx(k, "Wallpaper")[0])
            if p.is_file():
                return p
            # Slideshow / Spotlight: the original is not on record, but the
            # transcoded copy is a plain JPEG without an extension.
            import os
            t = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Themes" / "TranscodedWallpaper"
            if t.is_file():
                return t
        elif system == "Darwin":
            out = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to tell current desktop to get picture'],
                capture_output=True, text=True, check=True).stdout.strip()
            if out and Path(out).is_file():
                return Path(out)
        else:
            for key in ("picture-uri-dark", "picture-uri"):
                out = subprocess.run(["gsettings", "get", "org.gnome.desktop.background", key],
                                     capture_output=True, text=True).stdout.strip().strip("'")
                if out.startswith("file://"):
                    from urllib.parse import unquote, urlparse
                    p = Path(unquote(urlparse(out).path))
                    if p.is_file():
                        return p
    except Exception:
        pass
    sys.exit("Could not work out the current wallpaper on this system - pass the image as an argument.")


# --------------------------------------------------------------------------- #
# Output                                                                      #
# --------------------------------------------------------------------------- #

def write_files(profile: Path, image: Path, pal: dict) -> tuple[Path, Path]:
    chrome = profile / "chrome"
    chrome.mkdir(exist_ok=True)

    ext = image.suffix.lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".bmp"):
        ext = ".jpg"        # Firefox sniffs content, the name only needs to be plausible
    for stale in chrome.glob("livery-wallpaper.*"):
        stale.unlink()
    copy = chrome / f"livery-wallpaper{ext}"
    shutil.copyfile(image, copy)

    # ?v= defeats Firefox's image cache when the same name gets new bytes.
    url = f"{copy.name}?v={int(time.time())}"
    lines = [
        f"/* Generated by Wingman on {time.strftime('%Y-%m-%d %H:%M:%S')} from {image} - do not edit; Livery @imports this. */",
        ":root {",
        f'  --livery-wallpaper: url("{url}");',
        f"  --livery-accent: {hexs(pal['accent'])};",
        *[f"  --livery-palette-{i}: {hexs(c)};" for i, c in enumerate(pal["palette"])],
        f"  --livery-dominant: {hexs(pal['dominant'])};",
        "}",
        "",
    ]
    css = chrome / "livery-palette.css"
    tmp = css.with_suffix(".css.tmp")
    tmp.write_text("\n".join(lines), encoding="utf-8")
    tmp.replace(css)
    return copy, css


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", nargs="?", type=Path, help="image file (default: the current desktop wallpaper)")
    ap.add_argument("--profile", type=Path, help="Zen profile folder (default: the one Zen opens)")
    ap.add_argument("--dry-run", action="store_true", help="print the palette and write nothing")
    args = ap.parse_args()

    image = args.image or current_wallpaper()
    if not image.is_file():
        sys.exit(f"Not a file: {image}")

    pal = imint(image)
    print(f"image     {image}")
    print(f"accent    {hexs(pal['accent'])}   ({pal['coverage']:.1%} of the image is this hue)")
    print(f"palette   {'  '.join(hexs(c) for c in pal['palette'])}")
    print(f"dominant  {hexs(pal['dominant'])}")
    if args.dry_run:
        return

    profile = args.profile or find_profile()
    if not profile.is_dir():
        sys.exit(f"Profile folder not found: {profile}")
    copy, css = write_files(profile, image, pal)
    print(f"wrote     {copy}")
    print(f"wrote     {css}")
    print("Now restart Zen, or switch Livery off and on in Settings > Zen Mods.")


if __name__ == "__main__":
    main()
