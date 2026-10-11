#!/usr/bin/env python3
"""KZZ Football Live — static SEO page generator.

Reads predictions.json / news.json / analyses.json / teams_mm.json /
team_info.json in the site dir and generates indexable static pages:

  news/<id>.html                 one per news item (latest 60)
  predictions/<date>-<slug>.html  one per league+date
  analyses/<id>.html             one per post-match analysis
  leagues/<slug>.html            9 league hub pages
  teams/<slug>.html              25 curated team pages

Regenerates sitemap.xml with every page. Old dated pages (>30d for
predictions, beyond latest 60 for news) are pruned.

Run after any cron that updates the JSONs, BEFORE gh-pages-deploy.py.
"""
import html
import json
import os
import re
import sys
from datetime import date

SITE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://luuzoe.github.io/kzzfootballive"
ADS_CLIENT = "ca-pub-4388974491023298"
TODAY = date.today().isoformat()

LEAGUES = [
    ("premier-league", "Premier League", "အင်္ဂလန် ပရီးမီးယားလိဂ်", "🏴",
     "အင်္ဂလန်ရဲ့ ထိပ်တန်းလိဂ် — ကမ္ဘာပေါ်မှာ ပရိသတ်အများဆုံး လိဂ်တွေထဲက တစ်ခုဖြစ်ပြီး ချန်ပီယံဆုအတွက် နှစ်တိုင်း အပြင်းအထန် ယှဉ်ပြိုင်ကြတယ်။"),
    ("la-liga", "La Liga", "စပိန် လာလီဂါ", "🇪🇸",
     "စပိန်ရဲ့ ထိပ်တန်းလိဂ် — ရီးရဲလ်မက်ဒရစ်၊ ဘာစီလိုနာ၊ အက်သလက်တီကို မက်ဒရစ်တို့ ဗိုလ်စွဲနေကျ။ နည်းစနစ်ပိုင်း ကစားဟန်နဲ့ ကျော်ကြားတယ်။"),
    ("serie-a", "Serie A", "အီတလီ စီးရီးအေ", "🇮🇹",
     "အီတလီရဲ့ ထိပ်တန်းလိဂ် — ခံစစ်ခိုင်မာမှုနဲ့ နည်းဗျူဟာမြောက် ကစားဟန်ကြောင့် နာမည်ကြီး။ အင်တာမီလန်၊ အေစီမီလန်၊ ယူဗင်တပ်စ်၊ နာပိုလီတို့ ယှဉ်ပြိုင်ကြတယ်။"),
    ("bundesliga", "Bundesliga", "ဂျာမန် ဘွန်ဒက်စ်လီဂါ", "🇩🇪",
     "ဂျာမနီရဲ့ ထိပ်တန်းလိဂ် — ပရိသတ်အများဆုံး၊ ဂိုးအသွင်းအများဆုံး လိဂ်တွေထဲက တစ်ခု။ ဘိုင်ယန်မြူးနစ် ဗိုလ်စွဲနေကျဖြစ်ပေမဲ့ လေဗာကူဆင်၊ ဒေါ့မွန်တို့ စိန်ခေါ်နေတယ်။"),
    ("ligue-1", "Ligue 1", "ပြင်သစ် လီဂူး ၁", "🇫🇷",
     "ပြင်သစ်ရဲ့ ထိပ်တန်းလိဂ် — PSG လွှမ်းမိုးထားပေမဲ့ လူငယ်ကြယ်ပွင့်တွေ ပေါ်ထွက်ရာ လိဂ်။ မိုနာကို၊ မာဆေး၊ လိုင်ယွန်တို့ ရှိကြတယ်။"),
    ("eredivisie", "Eredivisie", "နယ်သာလန် အရီဒီဗီစီ", "🇳🇱",
     "နယ်သာလန်ရဲ့ ထိပ်တန်းလိဂ် — အေဂျက်စ်၊ PSV၊ ဖီယင်နော့ဒ်တို့ တိုက်စစ်ဖွင့် ကစားလေ့ရှိပြီး ဂိုးများတတ်တယ်။"),
    ("primeira-liga", "Primeira Liga", "ပေါ်တူဂီ ပရိုင်းရာလီဂါ", "🇵🇹",
     "ပေါ်တူဂီရဲ့ ထိပ်တန်းလိဂ် — ဘင်ဖီကာ၊ ပေါ်တို၊ စပို့တင်းတို့ သုံးသင်း ယှဉ်ပြိုင်ပွဲ။ ဥရောပ အသင်းကြီးတွေအတွက် ကြယ်ပွင့် မွေးထုတ်ပေးရာ လိဂ်။"),
    ("champions-league", "Champions League", "ချန်ပီယံလိဂ်", "⭐",
     "ဥရောပရဲ့ အမြင့်ဆုံး ကလပ်�ြိုင်ပွဲ — လိဂ် အသီးသီးက ထိပ်တန်း အသင်းတွေ ဖလား တစ်လုံးအတွက် ယှဉ်ပြိုင်ကြတယ်။"),
    ("europa-league", "Europa League", "ယူရိုပါလိဂ်", "🟠",
     "ဥရောပရဲ့ ဒုတိယအဆင့် ကလပ် ပြိုင်ပွဲ — ချန်ပီယံလိဂ် ဝင်ခွင့် လက်မှတ် တစ်နေရာအတွက် အသင်းတွေ အပြင်းအထန် တိုက်ကြတယ်။"),
]
LEAGUE_BY_NAME = {en: (slug, mm, icon) for slug, en, mm, icon, _ in LEAGUES}


def esc(s):
    return html.escape(str(s or ""), quote=True)


def paras(text):
    out = []
    for p in str(text or "").split("\n\n"):
        p = p.strip()
        if p:
            out.append("<p>" + esc(p).replace("\n", "<br>") + "</p>")
    return "\n".join(out)


def desc_of(text, n=150):
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    return esc(t[:n])


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "team"


ARTICLE_CSS = """
.article{max-width:760px;margin:0 auto;padding:16px}
.article h1{font-size:1.35rem;line-height:1.5;margin:8px 0}
.article .meta{color:#8aa392;font-size:.85rem;margin-bottom:12px}
.article p{line-height:1.85;margin:0 0 14px}
.crumbs{max-width:760px;margin:0 auto;padding:12px 16px 0;font-size:.85rem;color:#8aa392}
.crumbs a{color:#7fd79a}
.rel{margin-top:24px;border-top:1px solid #1e3a28;padding-top:12px}
.rel h2{font-size:1rem;margin-bottom:8px}
.rel ul{list-style:none;padding:0;margin:0}
.rel li{margin:6px 0}
.rel a{color:#b9f0c9}
.badge{display:inline-block;padding:2px 10px;border-radius:12px;font-size:.8rem;margin-right:6px}
.b-high{background:#14532d}.b-medium{background:#713f12}.b-low{background:#374151}
.prob{margin:8px 0}
.prob .row{display:flex;align-items:center;gap:8px;margin:4px 0;font-size:.85rem}
.prob .bar{height:8px;border-radius:4px;background:linear-gradient(90deg,#22c55e,#4ade80)}
.match{border:1px solid #1e3a28;border-radius:10px;padding:12px;margin:12px 0;background:#0f1f16}
.match h3{margin:0 0 6px;font-size:1.05rem}
"""

PAGE = """<!DOCTYPE html>
<html lang="my">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ | KZZ Football Live</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__CANON__">
<meta property="og:type" content="article">
<meta property="og:site_name" content="KZZ Football Live">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__CANON__">
<meta property="og:image" content="https://luuzoe.github.io/kzzfootballive/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=__ADS__" crossorigin="anonymous"></script>
<link rel="stylesheet" href="/styles.css?v=11">
<style>__CSS__</style>
</head>
<body>
<header class="site-header"><div class="header-inner"><div class="brand">
<a href="/" style="color:inherit;text-decoration:none;display:flex;align-items:center;gap:10px">
<span class="brand-ball">⚽</span><span><strong>KZZ Football Live</strong><br>
<span style="font-size:.8rem;color:#8aa392">ဘောလုံးတိုက်ရိုက် — Live Scores • Predictions • News</span></span></a>
</div></div></header>
<nav class="crumbs">__CRUMBS__</nav>
<main class="content article">
<h1>__H1__</h1>
<div class="meta">__META__</div>
__BODY__
<div class="ad-slot"><ins class="adsbygoogle" style="display:block" data-ad-client="__ADS__" data-ad-format="auto" data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>
__RELATED__
</main>
<footer class="site-footer">
<p>__FOOTLINKS__</p>
<p><a href="/about.html">About</a> • <a href="/privacy.html">Privacy Policy</a></p>
<p>KZZ Football Analysis • ဒေတာ — ESPN public API</p>
</footer>
</body></html>
"""

FOOTLINKS = " • ".join(
    '<a href="/leagues/%s.html">%s</a>' % (slug, mm) for slug, _en, mm, _ic, _d in LEAGUES
)


def render(title, desc, canon, crumbs, h1, meta, body, related=""):
    p = PAGE
    p = p.replace("__TITLE__", esc(title)).replace("__DESC__", desc)
    p = p.replace("__CANON__", canon).replace("__CRUMBS__", crumbs)
    p = p.replace("__H1__", esc(h1)).replace("__META__", meta)
    p = p.replace("__BODY__", body).replace("__RELATED__", related)
    p = p.replace("__FOOTLINKS__", FOOTLINKS).replace("__CSS__", ARTICLE_CSS)
    p = p.replace("__ADS__", ADS_CLIENT)
    return p


def crumbs(*parts):
    # parts: [(label, url|None)]
    out = ['<a href="/">🏠 ပင်မ</a>']
    for label, url in parts:
        if url:
            out.append("› " + '<a href="%s">%s</a>' % (url, esc(label)))
        else:
            out.append("› " + esc(label))
    return " ".join(out)


def rel_block(title, links):
    if not links:
        return ""
    items = "\n".join('<li><a href="%s">%s</a></li>' % (u, esc(t)) for t, u in links)
    return '<div class="rel"><h2>%s</h2><ul>\n%s\n</ul></div>' % (esc(title), items)


def load(name, default):
    p = os.path.join(SITE, name)
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write(path, content):
    full = os.path.join(SITE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return "/" + path


def main():
    urls = [("/", TODAY, "hourly", "1.0"),
            ("/about.html", TODAY, "monthly", "0.5"),
            ("/privacy.html", TODAY, "monthly", "0.5")]

    news_d = load("news.json", {"news": []})
    pred_d = load("predictions.json", {"predictions": []})
    ana_d = load("analyses.json", {"analyses": []})
    teams_mm = load("teams_mm.json", {"teams": {}}).get("teams", {})
    team_info = load("team_info.json", {})

    name2mm = {}
    for tid, r in teams_mm.items():
        if r.get("en"):
            name2mm[r["en"].lower()] = r.get("mm", r["en"])

    def mm_name(en):
        return name2mm.get(str(en).lower(), en)

    news = sorted(news_d.get("news", []), key=lambda x: x.get("published", ""), reverse=True)[:60]
    analyses = ana_d.get("analyses", [])
    preds = pred_d.get("predictions", [])

    # ---------- news pages ----------
    os.makedirs(os.path.join(SITE, "news"), exist_ok=True)
    for n in news:
        nid = re.sub(r"[^a-z0-9\-]", "", str(n.get("id", ""))[:60].lower()) or "news"
        body = paras(n.get("body_mm", ""))
        meta = "📰 %s • ရင်းမြစ်: %s" % (esc(n.get("published", "")[:10]), esc(n.get("source", "")))
        other = [(x["title_mm"], "/news/%s.html" % re.sub(r"[^a-z0-9\-]", "", str(x.get("id", ""))[:60].lower()))
                 for x in news if x.get("id") != n.get("id")][:5]
        page = render(n.get("title_mm", "သတင်း"), desc_of(n.get("body_mm", "")),
                      "%s/news/%s.html" % (BASE, nid),
                      crumbs(("သတင်း", "/#news"), (n.get("title_mm", "")[:40], None)),
                      n.get("title_mm", ""), meta, body,
                      rel_block("📰 နောက်ထပ် သတင်းများ", other))
        urls.append((write("news/%s.html" % nid, page), TODAY, "daily", "0.8"))

    # ---------- prediction pages (per league + date) ----------
    groups = {}
    for p in preds:
        slug = LEAGUE_BY_NAME.get(p.get("league", ""), (slugify(p.get("league", "league")), p.get("league", ""), ""))[0]
        dkey = str(p.get("date", ""))[:10]
        groups.setdefault((dkey, slug, p.get("league", "")), []).append(p)
    os.makedirs(os.path.join(SITE, "predictions"), exist_ok=True)
    pred_pages = []
    for (dkey, slug, league_en), ms in sorted(groups.items()):
        ms.sort(key=lambda x: x.get("date", ""))
        _s, league_mm, icon = LEAGUE_BY_NAME.get(league_en, (slug, league_en, "⚽"))
        cards = []
        for m in ms:
            ko = str(m.get("date", ""))[:16].replace("T", " ")
            conf = m.get("confidence", "")
            badge = {"high": ("b-high", "ယုံကြည်မှု မြင့်"), "medium": ("b-medium", "ယုံကြည်မှု အလယ်"),
                     "low": ("b-low", "ယုံကြည်မှု နည်း")}.get(conf, ("b-low", esc(conf)))
            probs = ""
            if all(k in m for k in ("prob_home", "prob_draw", "prob_away")):
                rows = []
                for lbl, v in (("အိမ် (%s)" % mm_name(m["home"]), m["prob_home"]),
                               ("သရေ", m["prob_draw"]),
                               ("အဝေး (%s)" % mm_name(m["away"]), m["prob_away"])):
                    rows.append('<div class="row"><span style="min-width:120px">%s %s%%</span>'
                                '<span class="bar" style="width:%s%%"></span></div>' % (esc(lbl), v, v))
                probs = '<div class="prob">' + "".join(rows) + "</div>"
            cards.append(
                '<div class="match"><h3>%s 🆚 %s</h3>'
                '<div class="meta">🕐 %s (မြန်မာစံတော်ချိန်) • <span class="badge %s">%s</span></div>'
                '<p><strong>ခန့်မှန်းချက်:</strong> %s</p>%s%s</div>'
                % (esc(mm_name(m.get("home"))), esc(mm_name(m.get("away"))), esc(ko),
                   badge[0], badge[1], esc(m.get("pick", "")), probs, paras(m.get("reason_mm", ""))))
        title = "%s %s ခန့်မှန်းချက် (%s)" % (icon, league_mm, dkey)
        body = "".join(cards) + "<p style='color:#8aa392;font-size:.85rem'>(ခန့်မှန်းချက်သာ — သေချာတာ မဟုတ်)</p>"
        fname = "predictions/%s-%s.html" % (dkey, slug)
        others = [(x[0], x[1]) for x in pred_pages if league_en in x[0]][-5:]
        page = render(title, desc_of(ms[0].get("reason_mm", "")),
                      "%s/%s" % (BASE, fname),
                      crumbs(("ခန့်မှန်းချက်", "/#predictions"), (title, None)),
                      title, "🔮 KZZ Football Analysis • %d ပွဲ" % len(ms), body,
                      rel_block("🔮 %s နောက်ထပ် ခန့်မှန်းချက်များ" % league_mm, others))
        pred_pages.append((title, "/" + fname))
        urls.append((write(fname, page), TODAY, "daily", "0.8"))
    # prune prediction pages older than 30 days
    for fn in os.listdir(os.path.join(SITE, "predictions")):
        if re.match(r"^\d{4}-\d{2}-\d{2}-", fn) and fn[:10] < "2026-09-11":
            try:
                os.remove(os.path.join(SITE, "predictions", fn))
            except OSError:
                pass

    # ---------- analysis pages ----------
    os.makedirs(os.path.join(SITE, "analyses"), exist_ok=True)
    for a in analyses:
        aid = re.sub(r"[^a-z0-9\-]", "", str(a.get("id", ""))[:60].lower()) or "analysis"
        score = "%s %d – %d %s" % (mm_name(a.get("home")), a.get("home_score", 0),
                                   a.get("away_score", 0), mm_name(a.get("away")))
        body = "<p><strong>ရလဒ်:</strong> %s</p>" % esc(score) + paras(a.get("body_mm", ""))
        meta = "⚔️ %s • %s" % (esc(a.get("league_mm") or a.get("league", "")), esc(a.get("date", "")))
        other = [(x["title_mm"], "/analyses/%s.html" % re.sub(r"[^a-z0-9\-]", "", str(x.get("id", ""))[:60].lower()))
                 for x in analyses if x.get("id") != a.get("id")][:5]
        page = render(a.get("title_mm", "သုံးသပ်ချက်"), desc_of(a.get("body_mm", "")),
                      "%s/analyses/%s.html" % (BASE, aid),
                      crumbs(("သုံးသပ်ချက်", "/#analyses"), (a.get("title_mm", "")[:40], None)),
                      a.get("title_mm", ""), meta, body,
                      rel_block("⚔️ နောက်ထပ် သုံးသပ်ချက်များ", other))
        urls.append((write("analyses/%s.html" % aid, page), TODAY, "weekly", "0.7"))

    # ---------- league hub pages ----------
    os.makedirs(os.path.join(SITE, "leagues"), exist_ok=True)
    for slug, en, mm, icon, blurb in LEAGUES:
        lp = [t for t, u in pred_pages if en in t]
        ln = []
        for n in news:
            blob = (n.get("title_mm", "") + " " + n.get("body_mm", "")).lower()
            if en.lower() in blob or mm in blob:
                ln.append((n["title_mm"], "/news/%s.html" % re.sub(r"[^a-z0-9\-]", "", str(n.get("id", ""))[:60].lower())))
            if len(ln) >= 5:
                break
        body = paras(blurb)
        body += ('<p>📊 <a href="/#standings">အဆင့်ဇယား ကြည့်ရန်</a> • '
                 '📅 <a href="/#fixtures">ပွဲစဉ်</a> • ✅ <a href="/#results">ရလဒ်</a> — '
                 'ပင်မစာမျက်နှာမှာ တိုက်ရိုက် ကြည့်နိုင်ပါတယ်။</p>')
        page = render("%s %s — ခန့်မှန်းချက်၊ သတင်း၊ ရလဒ်" % (icon, mm), desc_of(blurb),
                      "%s/leagues/%s.html" % (BASE, slug),
                      crumbs((mm, None)),
                      "%s %s" % (icon, mm),
                      "KZZ Football Analysis • %s" % esc(en), body,
                      rel_block("🔮 %s ခန့်မှန်းချက်များ" % mm, lp[:5]) +
                      rel_block("📰 %s သတင်းများ" % mm, ln))
        urls.append((write("leagues/%s.html" % slug, page), TODAY, "weekly", "0.9"))

    # ---------- team pages ----------
    os.makedirs(os.path.join(SITE, "teams"), exist_ok=True)
    for tid, info in team_info.items():
        rec = teams_mm.get(tid, {})
        en = rec.get("en", "Team %s" % tid)
        mm = rec.get("mm", en)
        tslug = slugify(en)
        trophies = "".join("<li>%s × %s</li>" % (esc(t["t"]), t["c"])
                           for t in info.get("trophies", []) if t.get("c"))
        body = ("<p><strong>မြို့:</strong> %s • <strong>တည်ထောင်နှစ်:</strong> %s • "
                "<strong>ကွင်း:</strong> %s</p>"
                % (esc(info.get("city", "—")), esc(info.get("founded", "—")), esc(info.get("stadium", "—"))))
        if trophies:
            body += "<p><strong>🏆 ဆုဖလားများ:</strong></p><ul>" + trophies + "</ul>"
        tn = []
        for n in news:
            blob = n.get("title_mm", "") + " " + n.get("body_mm", "")
            if en.lower() in blob.lower() or (mm != en and mm in blob):
                tn.append((n["title_mm"], "/news/%s.html" % re.sub(r"[^a-z0-9\-]", "", str(n.get("id", ""))[:60].lower())))
            if len(tn) >= 5:
                break
        page = render("%s (%s) — သတင်း၊ ခန့်မှန်းချက်" % (mm, en), desc_of(body),
                      "%s/teams/%s.html" % (BASE, tslug),
                      crumbs((mm, None)),
                      "⭐ %s <span style='font-size:.9rem;color:#8aa392'>%s</span>" % (esc(mm), esc(en)),
                      "KZZ Football Analysis", body,
                      rel_block("📰 %s သတင်းများ" % mm, tn))
        urls.append((write("teams/%s.html" % tslug, page), TODAY, "weekly", "0.7"))

    # ---------- sitemap ----------
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, freq, pri in urls:
        sm.append("  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n"
                  "    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>"
                  % (BASE, loc, lastmod, freq, pri))
    sm.append("</urlset>")
    with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm))

    print("OK: %d urls in sitemap (%d news, %d prediction pages, %d analyses, %d leagues, %d teams)"
          % (len(urls), len([u for u in urls if u[0].startswith("/news/")]),
             len([u for u in urls if u[0].startswith("/predictions/")]),
             len([u for u in urls if u[0].startswith("/analyses/")]),
             len([u for u in urls if u[0].startswith("/leagues/")]),
             len([u for u in urls if u[0].startswith("/teams/")])))


if __name__ == "__main__":
    sys.exit(main())
