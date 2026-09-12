"""Create contact sheets for full-page visual QA of the paper render."""

from pathlib import Path
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
render_dir = ROOT / "paper" / "rendered_v2"
pages = sorted(render_dir.glob("page-*.png"), key=lambda path: int(path.stem.split("-")[-1]))

for group_start in range(0, len(pages), 5):
    group = pages[group_start : group_start + 5]
    thumbs = []
    for path in group:
        image = Image.open(path).convert("RGB")
        image.thumbnail((600, 850))
        thumbs.append((path, image.copy()))
    sheet = Image.new("RGB", (len(thumbs) * 620, 900), "#d8d8d8")
    draw = ImageDraw.Draw(sheet)
    for index, (path, image) in enumerate(thumbs):
        x = index * 620 + 10
        sheet.paste(image, (x, 35))
        draw.text((x, 8), path.stem, fill="black")
    output = render_dir / f"contact_{group_start + 1:02d}_{group_start + len(group):02d}.png"
    sheet.save(output)
