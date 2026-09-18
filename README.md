# Livery

![Livery on Zen: a blurred F-14 wallpaper behind the sidebar and bookmarks bar](https://raw.githubusercontent.com/ps-margin/livery/main/image.png)

Your wallpaper as Zen's window background, softly blurred and tinted in its own colours — plus
a few small refinements to the bookmarks bar, the address bar and the compact-mode sidebar
and toolbar. Every one of them is a switch in
**Settings → Zen Mods → Livery**. Zen's defaults are left alone for anything Livery doesn't
name.

A livery is an aircraft's paint scheme. This one is yours.

## What you get

| | Default |
| --- | --- |
| **Wallpaper** — your desktop image behind every empty tab and the sidebar, blurred and dimmed so text stays readable | on |
| **Tint** — Zen's own three-colour gradient recipe in colours pulled from the wallpaper (or from Zen's theme colour), laid faintly over it | on |
| **Address bar** — the floating popup is narrower (`44rem`) | on |
| **Toolbar** — stays visible while the tab is empty *(compact mode with the toolbar hidden)* | on |
| **Toolbar** — the sidebar starts below it while it is showing, so nothing on it is covered *(compact mode with the toolbar hidden)* | on |
| **Sidebar** — docked instead of floating on the empty tab and while the bookmarks panel (`Ctrl+B`) is open *(compact mode with the sidebar hidden)* | on |
| **Bookmarks bar** — icons only; hovering one slides its title out | on |
| **Bookmarks bar** — the bar wraps to a second row when full, instead of hiding items in the `»` menu | on |
| **Context menu** — the page right-click menu cut down to a daily-use set (list below) | **off** |

## Sidebar — docked when it matters, floating otherwise

Compact mode with the sidebar hidden keeps the window clean, but the floating sidebar slides
in over whatever sits at the left edge — and Firefox's bookmarks panel (`Ctrl+B`) sits exactly
there, so every pass of the mouse covered it. Livery keeps the sidebar *docked* (the layout
you get with compact mode off) in two situations and lets Zen float it the rest of the time:

- **On the empty tab** — a new window, or Zen starting up. Type a URL and go, and the sidebar
  floats again.
- **While the bookmarks panel is open.** Open it with `Ctrl+B`, `Ctrl`-click or middle-click
  the bookmarks you want as new tabs, `Ctrl+B` again, and the sidebar floats again. Zen
  reopens the panel at startup if it was open when you quit.

Compact mode itself is never toggled; the switch only changes how the sidebar is positioned.

## Requirements — read this one

- **Written for Zen 1.22.** Later versions will probably work; if Zen renames something, the
  affected switch just stops having an effect (see Notes).
- **The wallpaper, tint, bookmarks-bar and address-bar tweaks work in every layout.**
- **The two toolbar tweaks need compact mode with the toolbar hidden, the sidebar tweak
  compact mode with the sidebar hidden** (Settings → Look and Feel), in either the
  single-toolbar or the multiple-toolbars layout. In any other layout they do nothing at
  all — the rules never match, nothing breaks, Zen behaves as it does without Livery.
- **Livery should be the first enabled mod in your list** (or the only one). It reads the
  palette file with an `@import`, which CSS only honours at the top of a stylesheet; Zen
  merges enabled mods in order.

## Getting your wallpaper in — three ways

Zen mods are pure CSS. A stylesheet cannot open a file picker or read your desktop settings,
so the wallpaper has to be *handed* to Livery. Pick one:

### 1. Wingman (recommended) — one command, does everything

`wingman.py` finds your current wallpaper, copies it into your Zen profile, works out its
colours, and writes the small file Livery reads. Run it again whenever you change wallpaper.

It runs on Windows, macOS and Linux with [uv](https://docs.astral.sh/uv/), which fetches
Python and the one image library it needs on first run — nothing to install by hand.

**Install uv** — the commands below are copied verbatim from uv's own installation page,
<https://docs.astral.sh/uv/getting-started/installation/> — check them there if you like:

```sh
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or through a package manager you already have: `brew install uv` ·
`winget install --id=astral-sh.uv -e` · `scoop install main/uv` · `pipx install uv`.
The docs note you can inspect the script before running it (`curl -LsSf https://astral.sh/uv/install.sh | less`).

**Then run Wingman** (download `wingman.py` from this repository first):

```sh
uv run wingman.py                 # current desktop wallpaper
uv run wingman.py photo.jpg       # a specific image
uv run wingman.py --dry-run       # just show the colours it would pick
```

Restart Zen, or switch Livery off and on in Settings → Zen Mods, and the background is in.
Already have Python 3.10+ with Pillow? `python wingman.py` works too.

Wallpaper detection: Windows (registry), macOS (System Events), GNOME (`gsettings`). On
other desktops pass the image as an argument. **Tested on Windows.** The macOS and Linux
detection and profile lookup follow the documented locations but have not been run on a
real machine yet — if it fails for you, pass the image and `--profile` explicitly and open
an issue.

### 2. Type an image URL

No script, no colour extraction — just the picture. Put the whole `url("…")` in the
**Wallpaper: image URL** field and Livery uses that image as the background: a file on your
machine, or an image on the web. Because nothing looks *at* the image this way, the tint
cannot be pulled from it; it comes from Zen's theme colour, or from the two hex fields if
you fill them in. Want the colours to match automatically? That is what Wingman is for.

| | Example |
| --- | --- |
| Windows | `url("file:///C:/Users/you/Pictures/wall.jpg")` |
| macOS | `url("file:///Users/you/Pictures/wall.jpg")` |
| Linux | `url("file:///home/you/Pictures/wall.jpg")` |
| Web | `url("https://example.com/wall.jpg")` — should work, not tested |

Forward slashes, three slashes after `file:`, and the quotes. The tint then comes from Zen's
theme colour (below) unless you fill in the two tint colour fields.

### 3. Nothing

Turn **Wallpaper** off. The bookmarks, address-bar, sidebar and toolbar tweaks work on their own.

## Colours — where the tint comes from

First match wins:

1. **Tint colour A / B** fields, if you filled them in (hex, e.g. `#2d95a9`).
2. **Wingman's palette** — the most vivid colour with real coverage, and the next best two
   at least 40° of hue away, lightness normalised so they read as UI colours.
3. **Zen's theme colour.** If you have picked a theme in Zen's theme picker (the palette
   button), that theme's main colour. If you haven't, Zen uses your operating system's
   accent colour — so on Windows with *Accent colour: Automatic*, the tint follows your
   wallpaper with no help at all.

How they are laid on: the same shape Zen's theme picker draws for a three-colour theme
(`ZenGradientGenerator.mjs`) — colour A as a soft glow from the top-left corner, colour B
from the bottom-right, the third palette colour as a shallow diagonal wash between them —
but at a fraction of Zen's opacity, over a light darkening scrim, so the wallpaper keeps its
own colours and only leans toward the palette at the corners.

## Settings reference

| Setting | Notes |
| --- | --- |
| Wallpaper: blur | CSS length. `0px` for sharp, `8px` default, `20px` is very soft |
| Wallpaper: darken | `0` = the image as is, `1` = black, `0.35` default. Raise it if text is hard to read |
| Address bar: popup width | CSS length or percentage: `44rem`, `720px`, `60%` |
| Bookmarks bar: wrap | While a second row exists, the sidebar (single toolbar + compact mode) starts one row too high and its top sits under the bookmarks — CSS can't measure the bar. With icon-only bookmarks a row holds dozens, so this rarely comes up |

The bookmarks bar, icons only until you hover one:

![The bookmarks bar with one bookmark's title slid out on hover](https://raw.githubusercontent.com/ps-margin/livery/main/docs/bookmarks-hover.png)

## Context menu: minimal

Off by default because it is one person's list. Zen 1.22's page menu has 122 entries; with
this on, right-clicking a page, link, image, video or text field shows only:

| Where | What stays |
| --- | --- |
| top row | Back · Forward · Reload · Bookmark (Zen's own icon row, untouched) |
| link | Open Link in New Container Tab / Open in Container ▸ · Open Link in Split View · Open Link in Smart Window · Copy Link |
| image / video | Open Image in New Tab · Save Video As · Save Audio As · Take Snapshot |
| selection | Search *engine* for "…" · Copy Clean Link to Highlight |
| text field | Undo · Redo · Cut · Copy · Paste · Delete · Select All |
| developer | View Page Source · Inspect |

Everything else — open in new tab/window/private window, bookmark link, save/copy image,
email, send to device, translate, ask AI, print, screenshot, spelling, playback speed, frames,
saved logins — is hidden while the switch is on. Keyboard shortcuts are unaffected. Tab and
sidebar right-click menus are not touched.

## Notes

- Livery targets Zen 1.22. Zen renames things between releases; if a tweak stops working,
  switch it off in the settings and open an issue with your Zen version.
- Nothing here touches web pages: everything is Zen's own chrome.
- Licence: MIT for this repository. Mods in the Zen registry are distributed under
  [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) per the registry's terms.

## Contact

Bugs, wrong claims, feature requests: open an issue here, or email **ps-margin@pm.me**.

## Credits

A large share of this — the research into how Zen loads mods, the palette heuristic, the
CSS, and most of this readme — was written together with Claude, Anthropic's model, over one
long evening. It was thorough, but it is not a Zen developer and neither am I: if you find a
mistake, email me at the address above, or **noreply@anthropic.com**. Yes, it's a no-reply
address. It seemed only fair that the co-author be reachable at the same one it signs its
commits with.

## Changelog

- **1.2.0** — sidebar: docked on the empty tab and while the bookmarks panel is open. The
  floating sidebar and toolbar now show the slice of the wallpaper they cover, not the middle
  of it. Tint redrawn as Zen's three-colour gradient; blur and darken defaults lowered
  (`8px`, `0.35`). The two toolbar switches now also work in the multiple-toolbars layout.
- **1.1.0** — context menu: minimal (off by default).
- **1.0.0** — first release.
