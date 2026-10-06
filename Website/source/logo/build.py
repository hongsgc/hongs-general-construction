"""Rebuild the ChatGPT Hong's logo as clean vector: roof + lettering as paths (Bevan, OFL)."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
import base64, io
from PIL import Image

F = TTFont("fonts/Bevan-Regular.ttf"); GS = F.getGlyphSet(); CMAP = F.getBestCmap()
RED = "#E41E20"

def text_path(s, cx, ybase, cap_px, sx=1.0):
    """Lay out s centred on cx, cap height cap_px, horizontal stretch sx."""
    names = [CMAP[ord(c)] for c in s]
    bp = BoundsPen(GS); GS[names[0]].draw(bp); lsb = bp.bounds[0]
    bp = BoundsPen(GS); GS[names[-1]].draw(bp); rsb = GS[names[-1]].width - bp.bounds[2]
    ink = sum(GS[n].width for n in names) - lsb - rsb
    ky = cap_px / F["OS/2"].sCapHeight; kx = ky * sx
    x0 = cx - ink * kx / 2
    pen = SVGPathPen(GS); x = -lsb
    for n in names:
        GS[n].draw(TransformPen(pen, (kx, 0, 0, -ky, x0 + x * kx, ybase))); x += GS[n].width
    return pen.getCommands(), (x0, x0 + ink * kx)

def roof(color):
    return f'''<g fill="{color}">
  <polygon points="345,218 768,26 1182,218 1164,226 768,48 363,226"/>
  <rect x="706" y="98" width="52" height="42"/><rect x="766" y="98" width="52" height="42"/>
  <rect x="706" y="148" width="52" height="42"/><rect x="766" y="148" width="52" height="42"/>
  <rect x="968" y="84" width="78" height="20"/><rect x="982" y="100" width="50" height="58"/>
</g>'''

def lettering(sub):
    h, _ = text_path("HONG\u2019S", 768, 388, 150, 1.1)
    g, _ = text_path("GENERAL CONSTRUCTION", 771, 490, 56)
    amp, (ax0, ax1) = text_path("&", 770, 556, 54 * 1592 / 1586)
    p, _ = text_path("PLUMBING", 767, 654, 83)
    return f'''<path fill="{RED}" d="{h}"/>
<path fill="{sub}" d="{g}"/>
<rect fill="{RED}" x="292" y="524" width="{ax0 - 14 - 292:.0f}" height="9"/><rect fill="{RED}" x="{ax1 + 14:.0f}" y="524" width="{1246 - ax1 - 14:.0f}" height="9"/>
<path fill="{RED}" d="{amp}"/>
<path fill="{sub}" d="{p}"/>'''

def svg(body, vb, bg=None):
    r = f'<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{" ".join(map(str,vb))}">{r}{body}</svg>'

PRIMARY_VB = (170, 8, 1200, 666)
open("out/hongs-logo-dark-bg.svg", "w").write(svg(roof(RED) + lettering("#FFFFFF"), PRIMARY_VB))
open("out/hongs-logo-light-bg.svg", "w").write(svg(roof(RED) + lettering("#1A1A1A"), PRIMARY_VB))

# full version: vector lettering over the original tool artwork (black ground only)
# tools: the original ChatGPT artwork with the old lettering blacked out, upscaled 4x with Real-ESRGAN (x4plus) -> tools-4x.jpg
tools_b64 = base64.b64encode(open("tools-4x.jpg", "rb").read()).decode()
img = f'<image width="1536" height="1024" xlink:href="data:image/jpeg;base64,{tools_b64}"/>'
open("out/hongs-logo-full-black.svg", "w").write(svg(img + roof(RED) + lettering("#FFFFFF"), (0, 0, 1536, 1024), "#000"))

# icon: the roof mark alone on black
hi, _ = text_path("H", 512, 900, 500, 1.05)
open("out/hongs-icon.svg", "w").write(svg(f'<g transform="translate({512 - 763.5 * 1.08:.1f} {70 - 26 * 1.08:.1f}) scale(1.08)">{roof(RED)}</g><path fill="{RED}" d="{hi}"/>', (0, 0, 1024, 1024), "#000"))
print("ok")
