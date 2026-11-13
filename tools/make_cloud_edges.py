"""The white cloud edge under the header: two tileable SVG strips (1200 x 64), puffs of different sizes.
The front one is solid white and runs into the page; the back one sits a little higher, half see-through."""
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]


def strip(widths, heights, base, fill, opacity=1.0):
    assert sum(widths) == 1200 and len(widths) == len(heights)
    x, d = 0, [f"M0 {base}"]
    for w, h in zip(widths, heights):
        c = base - 4 * h / 3  # a cubic with both handles at c peaks at h above the base
        d.append(f"C{x} {c:.1f} {x + w} {c:.1f} {x + w} {base}")
        x += w
    d.append("V64H0Z")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="64" viewBox="0 0 1200 64" preserveAspectRatio="none">'
            f'<path d="{" ".join(d)}" fill="{fill}" fill-opacity="{opacity}"/></svg>\n')


(SITE / "assets/cloud-front.svg").write_text(
    strip([170, 120, 210, 150, 190, 110, 250], [26, 18, 32, 22, 28, 16, 30], 46, "#ffffff"))
(SITE / "assets/cloud-back.svg").write_text(
    strip([230, 160, 140, 260, 180, 230], [30, 22, 18, 34, 24, 28], 40, "#ffffff", 0.55))
print("ok")
