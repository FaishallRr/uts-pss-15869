"""Generate arsitektur diagram + screenshot terminal untuk laporan UTS PSS."""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)

FONT_C = "C:/Windows/Fonts/consola.ttf"
FONT_CB = "C:/Windows/Fonts/consolab.ttf"
FONT_A = "C:/Windows/Fonts/arial.ttf"
FONT_AB = "C:/Windows/Fonts/arialbd.ttf"


# ==================================================================
# 1. DIAGRAM ARSITEKTUR (Soal 2a)
# ==================================================================
def draw_architecture():
    W, H = 1100, 620
    img = Image.new("RGB", (W, H), "#ffffff")
    d = ImageDraw.Draw(img)

    title_f = ImageFont.truetype(FONT_AB, 26)
    box_f = ImageFont.truetype(FONT_AB, 20)
    sub_f = ImageFont.truetype(FONT_A, 14)
    lbl_f = ImageFont.truetype(FONT_A, 15)

    d.text((W // 2, 22), "Arsitektur Simple LMS — User, Django, PostgreSQL",
           font=title_f, fill="#1a1a2e", anchor="mm")

    def box(x, y, w, h, title, lines, color, outline):
        d.rounded_rectangle([x, y, x + w, y + h], radius=12,
                            fill=color, outline=outline, width=3)
        d.text((x + w // 2, y + 30), title, font=box_f,
               fill="#111111", anchor="mm")
        for i, ln in enumerate(lines):
            d.text((x + w // 2, y + 62 + i * 22), ln, font=sub_f,
                   fill="#333333", anchor="mm")

    def arrow(x1, y1, x2, y2, label):
        d.line([x1, y1, x2 - 14, y2], fill="#444444", width=3)
        d.polygon([(x2, y2), (x2 - 16, y2 - 7), (x2 - 16, y2 + 7)],
                  fill="#444444")
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2 - 24
        tw = d.textlength(label, font=lbl_f)
        d.rectangle([mx - tw // 2 - 6, my - 11, mx + tw // 2 + 6, my + 11],
                    fill="#ffffff")
        d.text((mx, my), label, font=lbl_f, fill="#222222", anchor="mm")

    # User / Client
    box(40, 240, 230, 170, "User / Client",
        ["Browser (frontend)", "Mengirim HTTP request", "Menampilkan response"],
        "#dbeafe", "#2563eb")

    # Django app
    box(400, 120, 300, 380, "Aplikasi Django",
        ["config/ — settings & urls",
         "users/  — custom User + role",
         "catalog/ — Course, Lesson,",
         "  Enrollment, Assignment,",
         "  Submission (ORM)",
         "",
         "Django Admin: /admin",
         "Berjalan di container app"],
        "#dcfce7", "#16a34a")

    # PostgreSQL
    box(810, 240, 250, 170, "PostgreSQL",
        ["Database lms_db", "Container db", "Volume: postgres_data"],
        "#fef3c7", "#d97706")

    # Docker frame
    d.rounded_rectangle([370, 90, 730, 530], radius=14,
                        outline="#9ca3af", width=2)
    d.text((550, 105), "Container 'app' (port 8000)", font=sub_f,
           fill="#6b7280", anchor="mm")
    d.rounded_rectangle([785, 210, 1085, 430], radius=14,
                        outline="#9ca3af", width=2)
    d.text((935, 225), "Container 'db'", font=sub_f,
           fill="#6b7280", anchor="mm")

    arrow(275, 325, 395, 325, "HTTP request/response")
    arrow(705, 325, 805, 325, "SQL (ORM / psycopg)")

    d.text((W // 2, H - 22),
           "Docker Compose menyatukan service app + db dalam satu network",
           font=lbl_f, fill="#6b7280", anchor="mm")

    path = OUT / "arsitektur.png"
    img.save(path)
    print("OK:", path)


# ==================================================================
# 2. SCREENSHOT TERMINAL dari file bukti asli
# ==================================================================
def terminal_shot(txt_name, png_name, command, max_lines=34):
    src = BASE / "scripts_uts" / "out" / txt_name
    if not src.exists():
        print("SKIP (not found):", src)
        return
    lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
    lines = [ln for ln in lines if ln.strip() != ""]
    if len(lines) > max_lines:
        head = lines[: max_lines - 2]
        hidden = len(lines) - (max_lines - 2)
        lines = head + [f"  ... ({hidden} baris lainnya dipotong untuk laporan) ..."]

    font = ImageFont.truetype(FONT_C, 15)
    font_b = ImageFont.truetype(FONT_CB, 15)

    pad = 16
    line_h = 21
    # width = longest line
    longest = max([len(ln) for ln in lines] + [len(command)])
    W = int(longest * 8.4) + pad * 2
    W = max(W, 780)
    H = 78 + line_h * len(lines) + pad

    img = Image.new("RGB", (W, H), "#0c0c0c")
    d = ImageDraw.Draw(img)

    # Title bar
    d.rectangle([0, 0, W, 34], fill="#303030")
    d.ellipse([10, 10, 24, 24], fill="#e81123")
    d.ellipse([32, 10, 46, 24], fill="#f2a93b")
    d.ellipse([54, 10, 68, 24], fill="#6bb700")
    d.text((W // 2, 17), "Administrator: Windows PowerShell", font=font,
           fill="#cccccc", anchor="mm")

    y = 46
    # Command prompt
    d.text((pad, y), "PS D:\\MyProject\\UTS - PSS - 15869\\pss-minggu-4> ",
           font=font_b, fill="#5fd75f")
    d.text((pad + int(d.textlength("PS D:\\MyProject\\UTS - PSS - 15869\\pss-minggu-4> ", font=font_b)), y),
           command, font=font_b, fill="#f2f2f2")
    y += line_h + 6

    for ln in lines:
        # colorize
        if ln.startswith("===") or ln.startswith("---"):
            color = "#f2f2f2"
        elif "Query SQL" in ln or "Query SQL" in ln or "Jumlah Query" in ln:
            color = "#ffff00"
        elif ln.startswith("OK") or "READY" in ln or ln.startswith("System check"):
            color = "#5fd75f"
        elif ln.startswith("Index Scan") or "Seq Scan" in ln:
            color = "#5fd75f"
        elif "N+1" in ln or "SEBELUM" in ln or "AFTER" in ln or "BEFORE" in ln:
            color = "#f2f2f2"
        elif ln.startswith("  "):
            color = "#c0c0c0"
        else:
            color = "#d0d0d0"
        # truncate very long lines for image width
        display = ln
        if len(display) > 130:
            display = display[:127] + "..."
        d.text((pad, y), display, font=font, fill=color)
        y += line_h

    path = OUT / png_name
    img.save(path)
    print("OK:", path)


SHOTS = [
    ("q3a_compose_ps.txt", "shot_3a_compose_ps.png",
     "docker compose ps", 34),
    ("q4a_check_data.txt", "shot_4a_check_data.png",
     "docker compose exec app python manage.py shell", 40),
    ("q4b_queries.txt", "shot_4b_queries.png",
     "docker compose exec app python manage.py shell", 60),
    ("q5a_before.txt", "shot_5a_before.png",
     "docker compose exec app python manage.py shell", 34),
    ("q5b_after.txt", "shot_5b_after.png",
     "docker compose exec app python manage.py shell", 34),
    ("q5c_prefetch.txt", "shot_5c_prefetch.png",
     "docker compose exec app python manage.py shell", 40),
    ("q5d_explain.txt", "shot_5d_explain.png",
     "docker compose exec app python manage.py shell", 30),
    ("test_catalog.txt", "shot_test_catalog.png",
     "docker compose exec app python manage.py test catalog", 30),
]


if __name__ == "__main__":
    draw_architecture()
    for txt, png, cmd, mx in SHOTS:
        terminal_shot(txt, png, cmd, max_lines=mx)
    print("Done. Files in", OUT)
