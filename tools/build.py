"""Build the channel's site (GitHub Pages) from the films' projects: each film's making-of and storyboard as
standalone pages, and a front page listing the films.

The pages are made as claude.ai artifacts first (each project's making_of/index.html and storyboard/site/index.html),
which are written without a document head (the artifact host wraps them). Here each gets its own head: charset,
viewport, the same small reset the host adds, and link-preview tags. Their pictures and clips are copied beside them.

    python3 tools/build.py          rebuild the whole site from the projects (site.json: the site's address, the films)

The site is published as the channel, never as the person behind it: commits here are authored "Model & the Muse",
and nothing in a page names them (the making-of credits their words to a redaction bar).
"""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "site.json").read_text())
BASE = CONFIG["base"].rstrip("/")
FILMS = Path.home() / "projects" / "music_video"

RESET = (":root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);"
         "padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}"
         "body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#faf9f5;"
         "color:#141413}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}")


def head(title, description, url, image):
    e = html.escape
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
            f"<style>{RESET}</style>\n"
            f"<meta name=\"description\" content=\"{e(description)}\">\n"
            f"<meta property=\"og:type\" content=\"website\">\n<meta property=\"og:title\" content=\"{e(title)}\">\n"
            f"<meta property=\"og:description\" content=\"{e(description)}\">\n"
            f"<meta property=\"og:url\" content=\"{e(url)}\">\n<meta property=\"og:image\" content=\"{e(image)}\">\n"
            "<meta name=\"twitter:card\" content=\"summary_large_image\">\n"
            "<link rel=\"icon\" href=\"/mark.png\">\n")


def standalone(src, split, title, description, url, image):
    """An artifact page with a head of its own: its <title>, fonts and styles move into the head."""
    page = src.read_text()
    assert "<!doctype" not in page.lower()[:200], f"{src} already has a document head"
    split = next((m for m in (split if isinstance(split, tuple) else (split,)) if m in page), None)
    assert split, f"{src}: none of the markers where its body starts"
    top, body = page.split(split, 1)
    return head(title, description, url, image) + top.strip() + "\n</head>\n<body>\n" + split.strip() + body + "\n</body>\n</html>\n"


def copy_dir(src, dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def film(f):
    proj = FILMS / f["project"]
    out = ROOT / f["slug"]
    out.mkdir(exist_ok=True)
    url = f"{BASE}/{f['slug']}/"
    for d in ("img", "clips"):
        copy_dir(proj / "making_of" / d, out / d)
    (out / "index.html").write_text(standalone(
        proj / "making_of" / "index.html", "\n<main>", f"Making {f['title']}", f["making_of"], url,
        f"{url}img/hero.jpg"))
    sb = out / "storyboard"
    sb.mkdir(exist_ok=True)
    copy_dir(proj / "storyboard" / "site" / "frames", sb / "frames")
    (sb / "index.html").write_text(standalone(
        proj / "storyboard" / "site" / "index.html", ('\n<div class="wrap">', '\n<main class="wrap">'),
        f"{f['title']} Storyboard",
        f["storyboard"], f"{url}storyboard/", f"{url}storyboard/frames/{f['storyboard_image']}"))
    shutil.copyfile(proj / f["poster"], out / "poster.jpg")
    print(f"{f['slug']}/: the making-of, the storyboard, the poster")


def front():
    films = "\n".join(f"""    <article class="film">
      <a class="poster" href="{f['video']}"><img src="{f['slug']}/poster.jpg" width="1280" height="720" alt="{html.escape(f['poster_alt'])}"></a>
      <div class="about">
        <h2>{html.escape(f['title'])}</h2>
        <p class="credit">{html.escape(f['credit'])} · {html.escape(f['length'])}</p>
        <p>{html.escape(f['about'])}</p>
        <p class="links"><a href="{f['video']}">Watch the film</a><a href="{f['slug']}/">The making-of</a><a href="{f['slug']}/storyboard/">The storyboard</a></p>
      </div>
    </article>""" for f in CONFIG["films"])
    page = head("Model & the Muse", CONFIG["about"], f"{BASE}/", f"{BASE}/mark.png") + """<title>Model &amp; the Muse</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap">
<style>
/* Layout: the channel's mark and one line about it, then each film as a poster with its three links. Dark slate
   like the mark's ground, the wool's blue as the one accent. */
:root {
  color-scheme: dark;
  --ground: #1e2530; --raised: #262f3c; --rule: #364152; --text: #d9dee6; --muted: #98a3b3; --wool: #6f93ff;
  --display: "Young Serif", Georgia, serif; --body: "Atkinson Hyperlegible", "Helvetica Neue", Arial, sans-serif;
}
* { box-sizing: border-box; }
body { background: var(--ground); color: var(--text); font: 400 1.0625rem/1.6 var(--body); padding-inline: clamp(16px, 5vw, 48px); padding-block: 48px 72px; }
main { max-width: 980px; margin: 0 auto; display: grid; gap: 56px; }
header { display: grid; grid-template-columns: auto 1fr; gap: 20px 28px; align-items: center; }
header img { width: clamp(88px, 14vw, 128px); height: auto; border-radius: 6px; }
h1 { margin: 0; font: 400 clamp(2rem, 5vw, 3.2rem)/1.05 var(--display); text-wrap: balance; }
header p { margin: 0.6rem 0 0; color: var(--muted); max-width: 60ch; }
.film { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 28px; align-items: start; padding-top: 28px; border-top: 1px solid var(--rule); }
.poster img { display: block; width: 100%; height: auto; border-radius: 4px; }
.poster:focus-visible, .links a:focus-visible { outline: 2px solid var(--wool); outline-offset: 3px; }
h2 { margin: 0; font: 400 1.7rem/1.15 var(--display); text-wrap: balance; }
.credit { margin: 0.35rem 0 0.9rem; color: var(--muted); font-size: 0.95rem; letter-spacing: 0.02em; }
.about p { margin: 0 0 0.9rem; }
.links { display: flex; flex-wrap: wrap; gap: 8px 20px; }
.links a { color: var(--wool); text-underline-offset: 3px; }
footer { color: var(--muted); font-size: 0.9rem; border-top: 1px solid var(--rule); padding-top: 20px; }
footer a { color: var(--muted); }
@media (max-width: 720px) { .film { grid-template-columns: 1fr; } header { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<main>
  <header>
    <img src="mark.png" width="400" height="400" alt="An ampersand made of one strand of blue wool on a dark slate ground.">
    <div>
      <h1>Model &amp; the Muse</h1>
      <p>""" + html.escape(CONFIG["about"]) + """</p>
    </div>
  </header>
""" + films + """
  <footer><p><a href=\"""" + CONFIG["channel"] + """\">The channel on YouTube</a></p></footer>
</main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page)
    print("index.html: the front page")


def main():
    from PIL import Image
    Image.open(FILMS / CONFIG["mark"]).convert("RGB").resize((400, 400), Image.LANCZOS).save(ROOT / "mark.png")
    for f in CONFIG["films"]:
        film(f)
    front()
    (ROOT / ".nojekyll").write_text("")


if __name__ == "__main__":
    main()
