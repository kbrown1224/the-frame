from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_FONT = Path(__file__).parent / "fonts" / "Lora-Regular.ttf"
_MARGIN = 44
_GAP = 20          # space between quote block and author line
_LINE_LEADING = 6  # extra pixels between lines
_MAX_WIDTH = 600 - _MARGIN * 2   # 512px
_MAX_QUOTE_H = 264                # leaves room for margins + gap + author


def _require_font():
    if not _FONT.exists():
        raise FileNotFoundError(
            f"Font not found: {_FONT}\n"
            "Download Lora-Regular.ttf from fonts.google.com/specimen/Lora "
            "and save it to src/the_frame/fonts/Lora-Regular.ttf"
        )


def _wrap(draw, text, font):
    words = text.split()
    lines, current = [], []
    for word in words:
        probe = " ".join(current + [word])
        if draw.textlength(probe, font=font) <= _MAX_WIDTH:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _line_h(draw, font):
    _, top, _, bottom = draw.textbbox((0, 0), "Ag", font=font)
    return bottom - top + _LINE_LEADING


def _fit_font(draw, text):
    for size in range(36, 12, -2):
        font = ImageFont.truetype(str(_FONT), size)
        lines = _wrap(draw, text, font)
        if _line_h(draw, font) * len(lines) <= _MAX_QUOTE_H:
            return font, lines
    font = ImageFont.truetype(str(_FONT), 14)
    return font, _wrap(draw, text, font)


def render_quote(text, author):
    _require_font()

    img = Image.new("RGB", (600, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    q_font, lines = _fit_font(draw, text)
    a_font = ImageFont.truetype(str(_FONT), max(14, round(q_font.size * 0.65)))

    lh = _line_h(draw, q_font)
    ah = _line_h(draw, a_font)
    total_h = lh * len(lines) + _GAP + ah
    y = (400 - total_h) // 2

    for line in lines:
        x = (600 - round(draw.textlength(line, font=q_font))) // 2
        draw.text((x, y), line, fill=(0, 0, 0), font=q_font)
        y += lh

    y += _GAP
    author_str = f"— {author}"
    x = (600 - round(draw.textlength(author_str, font=a_font))) // 2
    draw.text((x, y), author_str, fill=(0, 0, 0), font=a_font)

    return img
