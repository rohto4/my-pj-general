from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tmp" / "ui-review" / "vikunja-listening-lounge" / "reacceptance"
OUT = ROOT / "tmp" / "ui-review" / "p0-review-2026-07-12"
YELLOW = (255, 212, 0)
FILL = (255, 212, 0, 34)


def font(size: int):
    candidates = [
        Path(r"C:\Windows\Fonts\meiryo.ttc"),
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size)
            except OSError:
                pass
    return ImageFont.load_default()


def annotate(source: str, target: str, boxes: list[tuple[tuple[int, int, int, int], str]]):
    image = Image.open(SOURCE / source).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    label_font = font(max(22, image.width // 90))
    for (x1, y1, x2, y2), label in boxes:
        draw.rectangle((x1, y1, x2, y2), outline=YELLOW + (255,), width=max(6, image.width // 320), fill=FILL)
        text_box = draw.textbbox((0, 0), label, font=label_font)
        tw = text_box[2] - text_box[0]
        th = text_box[3] - text_box[1]
        tx = min(max(0, x1), image.width - tw - 18)
        ty = max(0, y1 - th - 16)
        draw.rectangle((tx - 8, ty - 6, tx + tw + 8, ty + th + 6), fill=(22, 26, 36, 230))
        draw.text((tx, ty), label, fill=YELLOW + (255,), font=label_font)
    OUT.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(image, overlay).convert("RGB").save(OUT / target, quality=95)


def evidence_crop_comparison():
    before = Image.open(SOURCE / "project-list05-before.jpg").convert("RGB")
    after = Image.open(SOURCE / "project-list05-after.jpg").convert("RGB")
    panel_w = 640
    before_h = round(before.height * panel_w / before.width)
    after_h = round(after.height * panel_w / after.width)
    canvas_h = max(before_h, after_h) + 120
    canvas = Image.new("RGB", (panel_w * 2 + 40, canvas_h), (22, 26, 36))
    draw = ImageDraw.Draw(canvas)
    label_font = font(26)
    b = before.resize((panel_w, before_h), Image.Resampling.LANCZOS)
    a = after.resize((panel_w, after_h), Image.Resampling.LANCZOS)
    canvas.paste(b, (10, 70))
    canvas.paste(a, (panel_w + 30, 70))
    draw.text((20, 18), "BEFORE 1280x1400", fill=YELLOW, font=label_font)
    draw.text((panel_w + 40, 18), "AFTER 1280x587", fill=YELLOW, font=label_font)
    draw.rectangle((10, 70, panel_w + 10, 70 + before_h), outline=YELLOW, width=6)
    draw.rectangle((panel_w + 30, 70, panel_w + 30 + panel_w, 70 + after_h), outline=YELLOW, width=6)
    draw.rectangle((panel_w + 30, 70 + after_h, panel_w + 30 + panel_w, canvas_h - 14), outline=YELLOW, width=6)
    draw.text((panel_w + 48, 82 + after_h), "REVIEW: after is viewport-cropped", fill=YELLOW, font=font(22))
    OUT.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT / "05-evidence-crop-comparison.png", quality=95)


annotate(
    "project-dashboard01-after.jpg",
    "01-vikunja-dashboard-density-review.png",
    [
        ((250, 235, 2210, 475), "RV01 primary metrics"),
        ((250, 480, 2210, 720), "RV01 30-day calendar"),
        ((250, 735, 2210, 1375), "RV01 backlog / recent / views"),
    ],
)
annotate(
    "project-gantt02-after.jpg",
    "02-vikunja-gantt-empty-space-review.png",
    [
        ((260, 100, 2300, 255), "RV02 guide"),
        ((260, 255, 2300, 625), "RV02 date range / timeline"),
        ((260, 630, 2300, 1385), "RV02 empty vertical space"),
    ],
)
annotate(
    "project-kanban03-after.jpg",
    "03-vikunja-kanban-four-column-review.png",
    [
        ((260, 100, 2300, 255), "RV03 guide"),
        ((260, 255, 2300, 620), "RV03 four columns / scrollbars"),
        ((260, 625, 2300, 1375), "RV03 unused lower space"),
    ],
)
annotate(
    "task-detail04-after.jpg",
    "04-vikunja-task-detail-reading-order-review.png",
    [
        ((320, 85, 1380, 230), "RV04 title / metadata"),
        ((330, 430, 1375, 680), "RV04 description"),
        ((330, 690, 1375, 1035), "RV04 comment editor"),
        ((330, 1060, 1380, 1188), "RV04 action area"),
    ],
)
evidence_crop_comparison()
