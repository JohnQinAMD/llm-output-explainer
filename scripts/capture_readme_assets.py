#!/usr/bin/env python3
"""Capture the README screenshots and GIFs from the real demo page.

Dependencies: Playwright (with Chromium) and Pillow.
Run from the repository root:

    python3 scripts/capture_readme_assets.py
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PAGE_URL = (ROOT / "docs" / "index.html").as_uri()
OUT = ROOT / "media"


def wait_until_ready(page):
    page.wait_for_load_state("load")
    page.evaluate("document.fonts && document.fonts.ready")
    page.wait_for_timeout(250)


def set_theme(page, theme):
    page.evaluate("theme => { document.documentElement.dataset.theme = theme; }", theme)
    page.wait_for_timeout(80)


def save_gif(frame_paths, output, width, durations, colors=112):
    frames = []
    for path in frame_paths:
        image = Image.open(path).convert("RGB")
        height = round(image.height * width / image.width)
        frames.append(image.resize((width, height), Image.Resampling.LANCZOS))

    # One shared palette keeps the colors stable from frame to frame.
    thumb_width = max(1, width // 4)
    thumbs = [
        frame.resize(
            (thumb_width, round(frame.height * thumb_width / frame.width)),
            Image.Resampling.LANCZOS,
        )
        for frame in frames
    ]
    sheet = Image.new("RGB", (thumb_width, sum(image.height for image in thumbs)))
    y = 0
    for image in thumbs:
        sheet.paste(image, (0, y))
        y += image.height
    palette = sheet.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    indexed = [
        frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG)
        for frame in frames
    ]
    indexed[0].save(
        output,
        save_all=True,
        append_images=indexed[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )


def label_panel(image, label, dark=False):
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 21)
    except OSError:
        font = ImageFont.load_default()
    box = draw.textbbox((0, 0), label, font=font)
    width = box[2] - box[0] + 28
    fill = (230, 234, 242) if dark else (20, 26, 38)
    ink = (20, 26, 38) if dark else (251, 252, 254)
    draw.rounded_rectangle((18, 18, 18 + width, 54), radius=18, fill=fill)
    draw.text((32, 24), label, font=font, fill=ink)


def capture_simulator(browser, temp):
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(PAGE_URL)
    wait_until_ready(page)
    set_theme(page, "light")

    boxes = [
        page.locator(selector).bounding_box()
        for selector in (".controls", ".stepper", "#sim-fig .steptext")
    ]
    section = page.locator("#sim")
    section_box = section.bounding_box()
    top = round(boxes[0]["y"] - section_box["y"] - 12)
    bottom = round(boxes[2]["y"] + boxes[2]["height"] - section_box["y"] + 16)

    paths = []
    for index, step in enumerate((0, 1, 2, 3, 4)):
        page.locator("#step").evaluate(
            "(slider, value) => { slider.value = value; slider.dispatchEvent(new Event('input', {bubbles: true})); }",
            str(step),
        )
        page.wait_for_timeout(100)
        full_path = temp / f"simulator-full-{index}.png"
        path = temp / f"simulator-{index}.png"
        section.screenshot(path=full_path)
        with Image.open(full_path) as full:
            full.crop((0, top, full.width, bottom)).save(path)
        paths.append(path)

    save_gif(paths, OUT / "simulator.gif", 900, [850, 850, 850, 1100, 1700])
    page.close()


def capture_themes(browser, temp):
    page = browser.new_page(viewport={"width": 1000, "height": 650})
    page.goto(PAGE_URL)
    wait_until_ready(page)
    panels = []
    for theme in ("light", "dark"):
        set_theme(page, theme)
        path = temp / f"theme-{theme}.png"
        page.screenshot(path=path, clip={"x": 0, "y": 0, "width": 1000, "height": 650})
        panel = Image.open(path).convert("RGB").resize((640, 416), Image.Resampling.LANCZOS)
        label_panel(panel, theme.upper(), dark=theme == "dark")
        panels.append(panel)

    comparison = Image.new("RGB", (1280, 416))
    comparison.paste(panels[0], (0, 0))
    comparison.paste(panels[1], (640, 0))
    comparison.save(OUT / "theme-comparison.png", optimize=True)
    page.close()


def capture_selfcheck(browser, temp):
    page = browser.new_page(viewport={"width": 1120, "height": 720})
    page.goto(PAGE_URL + "#selfcheck")
    wait_until_ready(page)
    set_theme(page, "light")
    page.wait_for_timeout(150)

    paths = []
    clean = temp / "selfcheck-pass.png"
    page.screenshot(path=clean)
    paths.append(clean)

    # Add a deliberately oversized child at capture time. This does not alter
    # the demo; it proves that the page's real selfCheck() reports an overflow.
    page.evaluate(
        """
        () => {
          const box = document.createElement('div');
          box.id = 'capture-overflow';
          box.style.cssText = 'height:48px;width:100%;overflow:visible;margin-top:18px';
          const child = document.createElement('div');
          child.style.cssText = 'width:1450px;height:48px;background:var(--hot-wash);border:1px solid var(--hot);padding:10px;font:500 13px var(--font-mono)';
          child.textContent = 'Intentional capture-time overflow: 1450 px content inside the reading column';
          box.appendChild(child);
          document.querySelector('header').appendChild(box);
          window.dispatchEvent(new HashChangeEvent('hashchange'));
        }
        """
    )
    page.wait_for_timeout(120)
    broken = temp / "selfcheck-fail.png"
    page.screenshot(path=broken)
    paths.append(broken)

    save_gif(paths, OUT / "selfcheck.gif", 900, [1500, 2100], colors=96)
    page.close()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="llm-output-explainer-") as directory:
        temp = Path(directory)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            capture_simulator(browser, temp)
            capture_themes(browser, temp)
            capture_selfcheck(browser, temp)
            browser.close()
    for name in ("simulator.gif", "theme-comparison.png", "selfcheck.gif"):
        path = OUT / name
        print(f"{path.relative_to(ROOT)}: {path.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
