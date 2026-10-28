#!/usr/bin/env python3
"""Hong's General Construction & Plumbing bilingual street flyer.

Every string comes from Website/source/build_pages.py COPY (EN + the VI Hong
signed off 2026-10-09/10), so the flyer never says anything the site doesn't.
WA requires the contractor registration number on advertising: foot_reg.
Run: python3 build_flyer.py -> flyer-bi.html, PDF, 300dpi PNG.
"""
import base64, io, importlib.util, pathlib, subprocess
import qrcode, qrcode.image.svg
from PIL import Image

HERE = pathlib.Path(__file__).parent
WEB = HERE.parent / "Website"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = "Hong's General Construction Flyer - Bilingual"

spec = importlib.util.spec_from_file_location("site", WEB / "source" / "build_pages.py")
site = importlib.util.module_from_spec(spec); spec.loader.exec_module(site)
EN, VI = site.COPY["en"], site.COPY["vi"]

PHOTOS = [  # (file, EN label, VI label)
    ("work/residential-img-1751.jpg", EN["work_cats"]["residential"], VI["work_cats"]["residential"]),
    ("work/salons-bamboo-nails-254.jpg", EN["work_cats"]["salons"], VI["work_cats"]["salons"]),
    ("work/restaurants-1587f804-5a50-4d1c-8b34-ab8c07b83d5e.jpg", EN["work_cats"]["restaurants"], VI["work_cats"]["restaurants"]),
    ("hong-excavator.jpg", "", ""),
]


def jpg(path, max_w=1400):
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def logo():
    im = Image.open(WEB / "source" / "logo" / "hongs-logo-full-black.png").convert("RGB")
    mask = im.convert("L").point(lambda v: 255 if v > 24 else 0)
    im = im.crop(mask.getbbox())  # crop to ink on the black field
    im.thumbnail((1800, 1800))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def fonts():
    css = []
    for fam, files, w in (("Archivo", "archivo", "500 900"), ("Public Sans", "publicsans", "400 700")):
        for sub in ("latin", "latin-ext", "vietnamese"):
            data = base64.b64encode((WEB / "assets" / "fonts" / f"{files}-{sub}.woff2").read_bytes()).decode()
            stretch = "font-stretch:100% 125%;" if fam == "Archivo" else ""
            css.append(f"@font-face{{font-family:'{fam}';font-weight:{w};{stretch}"
                       f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")
    return "\n".join(css)


def qr(url):
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=0)
    return img.to_string(encoding="unicode")


CSS = """
@page { size: letter; margin: 0.3in; }
html, body { margin: 0; }
* { box-sizing: border-box; }
:root { --ink:#1A1C1E; --muted:#555B61; --line:#DEDFE0; --alt:#F4F2EF; --red:#E41E20; --redDark:#B3151A; }
body { font-family:'Public Sans', sans-serif; color:var(--ink); background:#fff;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.page { width:7.9in; height:10.4in; display:flex; flex-direction:column; gap:.14in; overflow:hidden; }
.d { font-family:'Archivo', sans-serif; font-weight:850; font-stretch:118%; letter-spacing:-.015em; }
.vn { display:block; color:var(--muted); font-weight:500; }

.hero { background:#000; color:#fff; border-radius:14px; padding:.2in .3in .2in; text-align:center; flex:0 0 auto; }
.hero img { width:3.0in; display:block; margin:0 auto; }
.hero h1 { font-size:21pt; line-height:1.08; margin:.12in 0 0; text-wrap:balance; }
.hero h1 .vn { color:#FF8A8B; font-family:'Public Sans'; font-weight:600; font-stretch:100%; letter-spacing:0; font-size:13.5pt; margin-top:5pt; }
.hero .eyebrow { font-size:10.5pt; color:#C9CCCF; margin:.1in 0 0; }

.photos { display:grid; grid-template-columns:1.5fr 1fr 1fr 1fr; gap:.08in; height:1.5in; flex:0 0 auto; }
.photos figure { margin:0; position:relative; border-radius:10px; overflow:hidden; }
.photos img { width:100%; height:100%; object-fit:cover; display:block; }
.photos figcaption { position:absolute; left:6pt; bottom:6pt; background:var(--red); color:#fff; border-radius:6px;
  padding:2pt 6pt; font-size:8.5pt; font-weight:700; line-height:1.2; }
.photos figcaption span { display:block; font-weight:500; }

.svc { display:grid; grid-template-columns:1fr 1fr; gap:.14in; flex:1 1 0; min-height:0; }
.card { border:2px solid var(--line); border-top:.09in solid var(--red); border-radius:12px; padding:.16in .2in; display:flex; flex-direction:column; }
.card .tags { margin-top:auto; padding-top:8pt; }
.card svg { width:.4in; height:.4in; flex:0 0 auto; color:var(--red); }
.card h2 { font-size:15.5pt; line-height:1.1; margin:4pt 0 0; }
.card h2 .vn { font-family:'Public Sans'; font-stretch:100%; letter-spacing:0; font-size:12pt; font-weight:600; margin-top:2pt; }
.card p { font-size:10pt; line-height:1.4; margin:6pt 0 0; }
.card p .vn { font-size:9.5pt; margin-top:2pt; }
.tags { display:flex; flex-wrap:wrap; gap:4pt; margin-top:7pt; }
.tags b { background:var(--alt); border-radius:99px; padding:3pt 9pt; font-size:9.5pt; font-weight:600; }
.tags b span { color:var(--muted); font-weight:500; }

.trust { display:grid; grid-template-columns:repeat(4,1fr); background:var(--red); color:#fff; border-radius:12px; flex:0 0 auto; }
.trust div { padding:.1in .12in; text-align:center; border-left:1px solid rgba(255,255,255,.35); }
.trust div:first-child { border-left:0; }
.trust b { display:block; font-size:12.5pt; line-height:1.15; }
.trust span { display:block; font-size:8.5pt; line-height:1.3; margin-top:2pt; color:#FFE1E1; }

.foot { background:#000; color:#fff; border-radius:14px; padding:.18in .24in; flex:0 0 auto;
  display:grid; grid-template-columns:1fr 1.3in; gap:.2in; align-items:center; }
.foot .cta { font-size:11pt; font-weight:600; color:#FF8A8B; margin:0; }
.foot .phone { font-size:34pt; line-height:1.05; margin:2pt 0 4pt; }
.foot .contact { font-size:11pt; margin:0; }
.foot .reg { font-size:8pt; color:#9EA3A8; margin:8pt 0 0; line-height:1.4; }
.qr { text-align:center; font-size:9pt; font-weight:600; }
.qr .box { background:#fff; padding:6pt; border-radius:8px; width:1.15in; margin:0 auto 4pt; }
.qr svg { width:100%; height:auto; display:block; }
"""


def both(en, vi):
    return f'{en}<span class="vn">{vi}</span>'


def build(assets):
    photos = "".join(f'<figure><img src="{src}" alt="">'
                     + (f'<figcaption>{en}<span>{vi}</span></figcaption>' if en else '') + '</figure>'
                     for src, en, vi in assets["photos"])
    def tags(a, b):
        return "".join(f"<b>{x} · <span>{y}</span></b>" for x, y in zip(a, b))
    trust = "".join(f"<div><b>{e[0]}</b><span>{v[0] if v[0] != e[0] else v[1]}</span></div>"
                    for e, v in zip(EN["trust"], VI["trust"]))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Hong's flyer (bilingual)</title>
<style>{assets['fonts']}{CSS}</style></head>
<body><div class="page">
  <section class="hero">
    <img src="{assets['logo']}" alt="{EN['logo_alt']}">
    <h1 class="d">{both(EN['h1'], VI['h1'])}</h1>
    <p class="eyebrow">{EN['eyebrow']}<br>{VI['eyebrow']}</p>
  </section>
  <section class="photos">{photos}</section>
  <section class="svc">
    <div class="card">{site.HOUSE_SVG}
      <h2 class="d">{both(EN['home_h'], VI['home_h'])}</h2>
      <div class="tags">{tags(EN['home_tags'], VI['home_tags'])}</div></div>
    <div class="card">{site.PIPE_SVG}
      <h2 class="d">{both(EN['plumb_h'], VI['plumb_h'])}</h2>
      <div class="tags">{tags(EN['plumb_tags'], VI['plumb_tags'])}</div></div>
  </section>
  <section class="trust">{trust}</section>
  <section class="foot">
    <div>
      <p class="cta">{EN['cta_quote']} · {VI['cta_quote']}</p>
      <p class="phone d">{site.PHONE}</p>
      <p class="contact">{site.EMAIL} · hongsgcpl.com</p>
      <p class="reg">{EN['foot_reg']}<br>{VI['foot_reg']}</p>
    </div>
    <div class="qr"><div class="box">{assets['qr']}</div>hongsgcpl.com</div>
  </section>
</div></body></html>"""


if __name__ == "__main__":
    img = WEB / "assets" / "img"
    assets = {
        "fonts": fonts(), "logo": logo(), "qr": qr(site.BASE),
        "photos": [(jpg(img / f, 1000), en, vi) for f, en, vi in PHOTOS],
    }
    html = HERE / "flyer-bi.html"
    html.write_text(build(assets), encoding="utf-8")
    pdf = HERE / f"{OUT}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html.as_uri()], check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", str(pdf), str(HERE / OUT)], check=True)
    print("wrote", pdf)
