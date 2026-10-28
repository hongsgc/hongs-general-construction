#!/usr/bin/env python3
"""Print collateral for Hong's General Construction & Plumbing.

Builds the van door magnet (18 x 12 in) and the bulletin-board flyer
(US Letter, English + Vietnamese) as self-contained HTML, then renders
PNG + PDF with headless Chrome. Shared facts live in one block below;
copy reuses the website's Hong-approved strings wherever possible.

    python3 Collateral/build.py
"""
import base64, io, subprocess
from pathlib import Path

import qrcode
import qrcode.image.svg
from PIL import Image

HERE = Path(__file__).resolve().parent
SITE = HERE.parent / "Website"
OUT = HERE / "out"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# ── Shared facts (one place; every piece reads these) ──────────────────
PHONE = "206-227-2275"
WEB = "hongsgcpl.com"
CC = "HONGSGC825B5"   # WA L&I construction contractor
PC = "HONGSGC791O7"   # WA L&I plumbing contractor
NAME = "Hong's General Construction & Plumbing"

RED, INK, MUTED, LINE = "#E41E20", "#1A1C1E", "#555B61", "#DEDFE0"

COPY = {
    "en": {
        "h1": "New construction and plumbing for homes and businesses.",
        "home_h": "New homes and commercial build-outs",
        "home_p": "We build new homes and commercial spaces like nail salons and restaurants. One contractor runs the whole project from start to finish.",
        "plumb_h": "Plumbing",
        "plumb_p": "Plumbing for houses and commercial buildings, from new installs to repairs. Call about any job, big or small.",
        "cap_home": "New home", "cap_salon": "Nail salon",
        "trust": [("35 years", "of experience"), ("Insured & bonded", "fully covered"), ("English · Tiếng Việt", "we speak both")],
        "call": "Call", "scan": "Scan to see our work",
        "area": "Based in Federal Way · serving the greater Seattle area",
        "reg": [("Construction contractor", CC), ("Plumbing contractor", PC)],
        "url": f"https://{WEB}/",
        "lang": "en",
    },
    "vi": {
        "h1": "Xây dựng mới và ống nước cho nhà ở và doanh nghiệp.",
        "home_h": "Xây dựng nhà ở và thương mại",
        "home_p": "Chúng tôi xây nhà mới và công trình thương mại như tiệm nail, nhà hàng. Một nhà thầu quản lý toàn bộ dự án từ đầu đến cuối.",
        "plumb_h": "Ống nước",
        "plumb_p": "Dịch vụ ống nước cho nhà ở và tòa nhà thương mại, từ lắp đặt mới đến sửa chữa. Việc lớn hay nhỏ, cứ gọi cho chúng tôi.",
        "cap_home": "Nhà ở", "cap_salon": "Tiệm nail",
        "trust": [("35 năm", "kinh nghiệm"), ("Bảo hiểm & bảo lãnh", "đầy đủ"), ("English · Tiếng Việt", "chúng tôi nói cả hai")],
        "call": "Gọi", "scan": "Quét mã để xem công trình",  # NEW string: needs Hong's read
        "area": "Trụ sở tại Federal Way · phục vụ khu vực Seattle",
        "reg": [("Nhà thầu xây dựng", CC), ("Nhà thầu ống nước", PC)],
        "url": f"https://{WEB}/vi/",
        "lang": "vi",
    },
}

PHOTO_HOME = SITE / "assets/img/work/residential-img-1751.jpg"
PHOTO_SALON = SITE / "assets/img/work/salons-dsc-2556.jpg"
LOGO = SITE / "source/logo/hongs-logo-light-bg.png"
FONTS = SITE / "assets/fonts"


def b64(data, mime):
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def logo_uri():
    im = Image.open(LOGO)
    im = im.crop(im.getbbox())  # crop to ink bounds before sizing
    buf = io.BytesIO(); im.save(buf, "PNG")
    return b64(buf.getvalue(), "image/png")


def photo_uri(p, w=1400):
    im = Image.open(p).convert("RGB"); im.thumbnail((w, w))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
    return b64(buf.getvalue(), "image/jpeg")


def qr_uri(url):
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=0)
    return b64(img.to_string(), "image/svg+xml")


def font_css():
    css = []
    for fam, stem, wt in [("Archivo", "archivo", "100 900"), ("Public Sans", "publicsans", "100 900")]:
        for sub in ["latin", "latin-ext", "vietnamese"]:
            f = FONTS / f"{stem}-{sub}.woff2"
            css.append(f"@font-face{{font-family:'{fam}';src:url({b64(f.read_bytes(), 'font/woff2')}) format('woff2');"
                       f"font-weight:{wt};font-stretch:62% 125%;font-display:block}}")
    return "\n".join(css)


BASE = """html,body{margin:0;padding:0;background:#fff}
*{box-sizing:border-box}
body{color:%s;font-family:'Public Sans',sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
h1,h2,.disp{font-family:'Archivo',sans-serif;font-weight:850;font-stretch:118%%;letter-spacing:-.015em;margin:0}
""" % INK


def magnet(L):
    # 18 x 12 in. Vendors print to the edge, so all content sits inside a 0.75 in safe zone.
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Door magnet</title><style>
{font_css()}
{BASE}
@page{{size:18in 12in;margin:0}}
.wrap{{width:18in;height:12in;padding:.3in}}
.sign{{width:100%;height:100%;padding:.45in .6in;display:flex;flex-direction:column;align-items:center;justify-content:space-between;
  border:.16in solid {RED};border-radius:.3in}}
.logo{{height:5in}}
.svc{{font-family:'Archivo';font-weight:800;font-stretch:112%;font-size:.5in;letter-spacing:.02em;color:{INK};text-transform:uppercase}}
.svc b{{color:{RED}}}
.phone{{font-family:'Archivo';font-weight:900;font-stretch:118%;font-size:1.55in;line-height:1;color:{INK};letter-spacing:-.01em}}
.row{{display:flex;gap:.6in;align-items:baseline;font-size:.42in;font-weight:700}}
.row .web{{color:{RED}}}
.reg{{font-size:.24in;color:{MUTED};font-weight:600}}
</style></head><body><div class="wrap"><div class="sign">
<img class="logo" src="{L}" alt="{NAME}">
<div class="svc">Homes <b>·</b> Businesses <b>·</b> Plumbing repairs</div>
<div class="phone">{PHONE}</div>
<div class="row"><span class="web">{WEB}</span><span>English · Tiếng Việt</span></div>
<div class="reg">WA Reg. {CC} · {PC} · Insured &amp; bonded</div>
</div></div></body></html>"""


def flyer(c, L, home, salon, qr):
    tabs = "".join(f'<div class="tab"><b>Hong\'s</b><span>{PHONE}</span></div>' for _ in range(8))
    trust = "".join(f"<div><strong>{a}</strong><span>{b}</span></div>" for a, b in c["trust"])
    reg = " · ".join(f"{a} {b}" for a, b in c["reg"])
    return f"""<!doctype html><html lang="{c['lang']}"><head><meta charset="utf-8"><title>Flyer {c['lang'].upper()}</title><style>
{font_css()}
{BASE}
@page{{size:8.5in 11in;margin:0}}
.page{{width:8.5in;height:11in;overflow:hidden;padding:.4in .45in .35in;display:flex;flex-direction:column}}
.logo{{display:block;height:1.35in;margin:0 auto .12in}}
h1{{font-size:.34in;line-height:1.08;text-align:center;text-wrap:balance;margin:0 .2in .2in}}
.photos{{display:grid;grid-template-columns:1fr 1fr;gap:.12in}}
.photos figure{{margin:0;position:relative}}
.photos img{{width:100%;height:2in;object-fit:cover;display:block;border-radius:.06in}}
.photos figcaption{{position:absolute;left:.08in;bottom:.08in;background:{INK};color:#fff;font-weight:700;font-size:.13in;padding:.03in .09in;border-radius:.04in}}
.svc{{display:grid;grid-template-columns:1fr 1fr;gap:.28in;margin:.16in 0 .14in}}
.svc h2{{font-size:.2in;line-height:1.15;margin-bottom:.05in;padding-top:.06in;border-top:.04in solid {RED}}}
.svc p{{margin:0;font-size:.135in;line-height:1.45;color:{MUTED}}}
.trust{{display:grid;grid-template-columns:repeat(3,1fr);background:{RED};color:#fff;border-radius:.06in;padding:.1in .1in}}
.trust div{{text-align:center;display:flex;flex-direction:column}}
.trust strong{{font-family:'Archivo';font-weight:850;font-stretch:112%;font-size:.19in}}
.trust span{{font-size:.12in;opacity:.92}}
.cta{{display:flex;align-items:center;justify-content:space-between;margin:.14in 0 .06in;gap:.3in}}
.call small{{display:block;font-weight:700;font-size:.17in;color:{MUTED};text-transform:uppercase;letter-spacing:.08em}}
.call .num{{font-family:'Archivo';font-weight:900;font-stretch:112%;font-size:.6in;line-height:1;white-space:nowrap}}
.call .web{{font-weight:700;font-size:.18in;color:{RED};margin-top:.04in}}
.qr{{display:flex;align-items:center;gap:.12in;font-size:.13in;font-weight:700;max-width:2.3in}}
.qr img{{width:1.05in;height:1.05in}}
.fine{{font-size:.105in;color:{MUTED};text-align:center;line-height:1.4}}
.tabs{{margin-top:auto;display:grid;grid-template-columns:repeat(8,1fr);border-top:1.5px dashed #9EA3A8;height:1.9in}}
.tab{{border-left:1.5px dashed #9EA3A8;writing-mode:vertical-rl;transform:rotate(180deg);display:flex;align-items:center;justify-content:center;gap:.06in;font-size:.13in;white-space:nowrap;padding:0}}
.tab:first-child{{border-right:1.5px dashed #9EA3A8}}
.tab b{{font-family:'Archivo';font-weight:850;color:{RED}}}
.tab span{{font-weight:700}}
</style></head><body><div class="page">
<img class="logo" src="{L}" alt="{NAME}">
<h1>{c['h1']}</h1>
<div class="photos">
  <figure><img src="{home}" alt=""><figcaption>{c['cap_home']}</figcaption></figure>
  <figure><img src="{salon}" alt=""><figcaption>{c['cap_salon']}</figcaption></figure>
</div>
<div class="svc">
  <div><h2>{c['home_h']}</h2><p>{c['home_p']}</p></div>
  <div><h2>{c['plumb_h']}</h2><p>{c['plumb_p']}</p></div>
</div>
<div class="trust">{trust}</div>
<div class="cta">
  <div class="call"><small>{c['call']}</small><div class="num">{PHONE}</div><div class="web">{WEB}</div></div>
  <div class="qr"><img src="{qr}" alt=""><span>{c['scan']}</span></div>
</div>
<div class="fine">{c['area']}<br>WA {reg}</div>
<div class="tabs">{tabs}</div>
</div></body></html>"""


def render(html_path, w_in, h_in, png_px_w):
    pdf = html_path.with_suffix(".pdf"); png = html_path.with_suffix(".png")
    url = html_path.as_uri()
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", url], check=True, capture_output=True)
    scale = png_px_w / (w_in * 96)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={int(w_in*96)},{int(h_in*96)}", f"--force-device-scale-factor={scale}",
                    f"--screenshot={png}", url], check=True, capture_output=True)
    return pdf, png


def main():
    OUT.mkdir(exist_ok=True)
    L = logo_uri()
    home, salon = photo_uri(PHOTO_HOME), photo_uri(PHOTO_SALON)
    p = OUT / "door-magnet-18x12.html"; p.write_text(magnet(L)); render(p, 18, 12, 2400)
    for lang, c in COPY.items():
        p = OUT / f"flyer-{lang}.html"; p.write_text(flyer(c, L, home, salon, qr_uri(c["url"]))); render(p, 8.5, 11, 1700)
    print("\n".join(str(f) for f in sorted(OUT.iterdir())))


if __name__ == "__main__":
    main()
