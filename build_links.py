"""
Title:        New Thought Nursery — One Link + Music page generator
Author:       Hali Sarah Parsons (I.Q. Productionz)
Date:         2026-10-24
Modified By:  Claude (Anthropic), for Hali Sarah Parsons
Description:  Builds Hosted/Links/ (main one-link page), /Music/ (clickable song list) and
              /Music/<Song>/ (one-link page per song) from a single SONGS table.
              WHY one table: every page reads the same data, so a new release is one
              new row and a rerun, and links can never drift out of sync between pages.
"""
import html, json, os, re, urllib.request

# WHY Hosted/: the live site lives in the Hosted folder next to this script. Keeping the
# script outside it means Cloudflare never publishes it, and it works from any folder.
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Hosted')
BASE = 'https://childrens.iqproductionz.com'

# Brand-level destinations (verified 2026-10-24)
SPOTIFY_ARTIST = 'https://open.spotify.com/artist/5lBDvcJaFh2c6KLmAkLvQ2'
YT_CHANNEL = 'https://www.youtube.com/@NewThoughtNursery'
YT_PLAYLIST = 'https://www.youtube.com/playlist?list=PLKe0i8vjcVZU'
YTM_PLAYLIST = 'https://music.youtube.com/playlist?list=PLKe0i8vjcVZU'
EMAIL = 'newthoughtnursery@gmail.com'

# (title as released, YouTube video id, Spotify track id, length) — playlist order
SONGS = [
 ("Ten Little Turtles (Remix)", "cCab2XLTTXU", "0bd8wfKP9MjJRHSaMVDfQO", "2:43"),
 ("Three Little Bats (Remix)", "abmpMVrKNkQ", "5813IpVSBXwCjZtK1Dmz1v", "2:06"),
 ("Big Yacht Cradle (Remix)", "q_vMwS0wmtU", "0lXkPYcf8uBFqdmV8Htg1B", "3:28"),
 ("We're Goin' On A Whale Watch (Remix)", "Yz50bvUTVDQ", "0zr8YPYPfpVcXMJZf9B0X5", "3:31"),
 ("Jack & Jill (Remix)", "KGh7sr0_x0c", "03ZvqPrEJUxBt5aiaAOapJ", "2:36"),
 ("London Bridge (Remix)", "okcRQKkykUk", "2xrYyflxavvgv2NjlVJyQv", "2:12"),
 ("Ring-Around-The-Mommy (Remix)", "7k72aU4ttmQ", "7nCHLocm1CygisbcntIyOD", "1:38"),
 ("Row Row Ocean (Remix)", "n8rp21O2oAw", "4ImvbOET3ZwGLXaE5r2B1F", "3:32"),
 ("Baa Baa Rainbow (Remix)", "cO-rq3CKzDM", "0771ZI14nkvsIAwt1yevvu", "2:32"),
 ("Giant Star Sparkle (Remix)", "495WfvSc3cA", "7dnMCQOCWl0meUhMwBIzce", "4:01"),
 ("All Through The Sky (Remix)", "NyIn8nZ5ljI", "6eZyH680G0Wm4QLiW1rzvc", "2:52"),
 ("Phone Activity Alphabet (Remix)", "Kz3WwHwLv00", "1QXt8jZiuUzp34VALVlKHy", "4:40"),
 ("Slow It Down", "yUc4fht5zdE", "2fCfYz60jvPhSSfmor79eN", "2:15"),
 ("Wanka Alphabet", "fQoPD6bBk9s", "0STxQ5hVD7sWqMvKCZtQIl", "1:26"),
 ("Ring-Around-The-Daddy (Remix)", "zdBxg9-25xw", "5M3WBAQPua065rzTbQ4KQM", "1:39"),
 ("I Love You Body", "8pr26rtOHQI", "7jo6Vi565nKtzbdrO5DucE", "4:11"),
 ("Mix It", "ZefQNZ-wCz8", "3PseoMYQd84DLZPT15o2NL", "2:30"),
 ("Blow Your Nose", "7Aq1eEKvSAk", "0OjxLRsyHcuTXhLWWPR4Ft", "2:59"),
 ("Change It", "QO2KlKw3Upo", "7pbEpG2ltID3geFbEdbFV7", "1:50"),
 ("Good Energy", "ot73bMJTYTY", "1XPFwqkQoqYRflEE3b6dq3", "3:47"),
 ("Spit Storm", "WTpzgBDKWqA", "2q2B9WsU4ff3S5nVwxOmiP", "4:04"),
 ("Alphabet Alliterations", "pykRSphtnl0", "02zw4j3vc3rGIJ5xEmxFSQ", "3:48"),
]

E = html.escape

# WHY borrow the wordmark from Contact/index.html: every page shares the exact same logo
# header as the homepage and Contact page, and a logo change there flows here on rebuild.
_contact = open(os.path.join(OUT, 'Contact', 'index.html'), encoding='utf-8').read()
WORDMARK = re.search(r'<svg class="wordmark".*?</svg>', _contact, re.S).group(0)

def brand(up):
    """Shared header mark: butterfly over the 'u' in Thought + wordmark, linking home.
    up = relative path back to the site root ('../' or '../../')."""
    return (f'<a class="mark" href="{up}" aria-label="New Thought Nursery home">'
            f'<img class="flutter" src="{up}Assets/butterfly.png" alt="">{WORDMARK}</a>')

def slug(title):
    """Folder name for a song. WHY capitalized words: Hali's site folders start with a
    capital letter (Assets/, Contact/), and '(Remix)' is dropped so URLs stay short."""
    t = re.sub(r'\s*\(Remix\)', '', title).replace('&', 'And').replace("'", '')
    return '-'.join(w[:1].upper() + w[1:] for w in re.findall(r'[A-Za-z0-9]+', t))

def short(title):
    """Display name without '(Remix)' for headings; the full release title stays in meta."""
    return re.sub(r'\s*\(Remix\)', '', title)

# Inline SVG icons. WHY inline: no icon font or extra request, and they inherit button color.
IC = {
 'spotify': '<path d="M12 1.5a10.5 10.5 0 1 0 0 21 10.5 10.5 0 0 0 0-21zm4.8 15.2a.65.65 0 0 1-.9.2c-2.5-1.5-5.6-1.9-9.3-1a.65.65 0 1 1-.3-1.3c4-.9 7.5-.5 10.3 1.2.3.2.4.6.2.9zm1.3-2.9a.82.82 0 0 1-1.1.3c-2.8-1.7-7.1-2.2-10.5-1.2a.82.82 0 1 1-.5-1.6c3.8-1.2 8.6-.6 11.8 1.4.4.2.5.7.3 1.1zm.1-3c-3.4-2-9-2.2-12.2-1.2a1 1 0 1 1-.6-1.9c3.7-1.1 9.9-.9 13.8 1.4a1 1 0 0 1-1 1.7z"/>',
 'youtube': '<path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .6 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .4-4.8 31 31 0 0 0-.4-4.8zM9.7 15.1V8.9L15.5 12z"/>',
 'ytmusic': '<path d="M12 1.5a10.5 10.5 0 1 0 0 21 10.5 10.5 0 0 0 0-21zm0 16.6a6.1 6.1 0 1 1 0-12.2 6.1 6.1 0 0 1 0 12.2zm0-11a4.9 4.9 0 1 0 0 9.8 4.9 4.9 0 0 0 0-9.8zM10 15V9l5 3z"/>',
 'list': '<path d="M3 5h12v2H3zm0 6h12v2H3zm0 6h8v2H3zm14-3V4h4v2h-2v10.5a2.5 2.5 0 1 1-2-2.45z"/>',
 'play': '<path d="M8 5v14l11-7z"/>',
 'home': '<path d="M12 3 2 11h3v9h5v-6h4v6h5v-9h3z"/>',
 'mail': '<path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm9 7.2L4 7.3V17h16V7.3z"/>',
 'book': '<path d="M5 3h11a3 3 0 0 1 3 3v15H7a2 2 0 0 1-2-2zm2 14v2h10v-2z"/>',
}
def icon(k): return f'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{IC[k]}</svg>'

def btn(href, label, k, cls='', ext=True):
    """One full-width link button. WHY rel=noopener on outside links: the opened tab can't
    script this page, and target=_blank keeps the one-link page open behind it."""
    t = ' target="_blank" rel="noopener"' if ext else ''
    return f'<a class="lk {cls}" href="{E(href)}"{t}>{icon(k)}<span>{E(label)}</span></a>'

# Shared styles: same tokens as the main site so these pages feel like part of it.
CSS = """
:root{
  /* WHY light-only: the brand is watercolor paper; colors match site/index.html tokens. */
  --paper:#FDFBF6;--ink:#2E2466;--ink-soft:#5A5288;--teal:#1F8584;--pink:#E07AA6;
  --mint:#C8EAD6;--sky:#C7EAF5;--blush:#F8C8D8;--butter:#FFF2B5;--night:#2B2556;
  --card-mint:#DBF1E4;--card-blush:#FBE1EA;
  --f-display:"Fraunces",Georgia,serif;--f-script:"Dancing Script",cursive;--f-body:"Nunito",system-ui,sans-serif;
  color-scheme:light;
}
*{box-sizing:border-box}
html,body{margin:0}
body{min-height:100vh;min-height:100dvh;display:flex;flex-direction:column;background:var(--paper);color:var(--ink);
  font:400 1rem/1.55 var(--f-body);
  /* WHY washes: echoes the flyer's watercolor bleed without loading an image */
  background-image:radial-gradient(30rem 20rem at 0% 0%,color-mix(in srgb,var(--sky) 60%,transparent),transparent 70%),
    radial-gradient(28rem 20rem at 100% 10%,color-mix(in srgb,var(--blush) 50%,transparent),transparent 70%)}
.top{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;text-align:center;
  padding:2rem max(16px,env(safe-area-inset-left)) 1.5rem}
.top > .mark{margin-bottom:.5rem}
/* Shared logo header — same values as the Contact page (.chead) so all pages match. */
.mark{display:block;width:min(30rem,100%);margin-inline:auto;text-decoration:none}
.mark:focus-visible{outline:3px solid var(--pink);outline-offset:3px}
/* Butterfly: lower-left wing lines up with the start of the "u" in Thought (39.4% across) */
.flutter{--bw:min(100px,24vw);width:var(--bw);margin:0 0 -.15rem calc(39.4% - var(--bw) * .115 + 3px);opacity:.9;display:block;
  animation:float 6s ease-in-out infinite}
@keyframes float{50%{transform:translateY(-8px) rotate(-2deg)}}
.wordmark{width:min(30rem,100%);height:auto;display:block;margin-inline:auto}
.name{font:700 1.6rem/1.15 var(--f-display);margin:.4rem 0 0}
.tag{font:600 1.35rem/1.2 var(--f-script);color:var(--teal);margin:.2rem 0 0}
.sub{color:var(--ink-soft);font-size:.92rem;margin:.35rem 0 0}
/* Bottom-heavy: the dark band holds every button and grows to fill the lower page. */
.band{background:var(--night);color:var(--card-blush);position:relative;padding:3.25rem 0 2.5rem}
.band::before{content:"";position:absolute;inset:-1px 0 auto;height:34px;background:var(--paper);
  -webkit-mask:radial-gradient(24px 18px at 50% 0,#000 98%,transparent) 0 0/48px 34px repeat-x;
          mask:radial-gradient(24px 18px at 50% 0,#000 98%,transparent) 0 0/48px 34px repeat-x}
.col{max-width:30rem;margin-inline:auto;padding-inline:max(16px,env(safe-area-inset-left)) max(16px,env(safe-area-inset-right))}
.eyebrow{font:700 .72rem/1 var(--f-body);letter-spacing:.14em;text-transform:uppercase;color:var(--card-mint);margin:1.5rem 0 .7rem;text-align:center}
.eyebrow:first-child{margin-top:0}
.lk{display:flex;align-items:center;gap:.75rem;padding:.95rem 1.15rem;margin-bottom:.7rem;border-radius:1rem;
  background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.2);color:#fff;text-decoration:none;font-weight:700;
  transition:transform .15s ease,background .15s ease}
.lk svg{width:1.4rem;height:1.4rem;flex:none}
.lk span{flex:1;min-width:0}
.lk:hover{transform:translateY(-2px);background:rgba(255,255,255,.13)}
.lk:focus-visible{outline:3px solid var(--card-mint);outline-offset:2px}
.lk.hero{background:var(--card-mint);border-color:var(--card-mint);color:var(--night)}
.lk.spotify svg{color:#1DB954}.lk.yt svg{color:#FF4E45}.lk.ytm svg{color:#FF6B6B}
.lk.hero svg{color:var(--night)}
.foot{text-align:center;font-size:.8rem;color:#BDB3E6;margin-top:1.75rem}
.foot a{color:#fff}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.back{display:inline-block;margin-top:.9rem;font-weight:700;color:var(--ink);font-size:.95rem}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

def page(path, title, desc, og_img, body, depth, extra_css=''):
    """Writes one page. depth = how many folders below site root, so relative asset paths
    work on Cloudflare Pages and when the files are opened locally."""
    up = '../' * depth
    url = BASE + '/' + path.rstrip('/') + '/' if path else BASE + '/'
    doc = f"""<!--
  Title:        {E(title)}
  Author:       Hali Sarah Parsons (I.Q. Productionz)
  Date:         2026-10-24
  Modified By:  Claude (Anthropic), for Hali Sarah Parsons
  Description:  {E(desc)}
                Generated by build_links.py — edit the SONGS table there, not this file.
-->
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#2B2556">
<link rel="icon" type="image/png" sizes="32x32" href="{up}Assets/favicon-32.png">
<link rel="apple-touch-icon" href="{up}Assets/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="New Thought Nursery">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{E(og_img)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Fraunces:opsz,wght@9..144,700&family=Nunito:wght@400;700&display=swap">
<style>{CSS}{extra_css}</style>
</head>
<body>
{body}
</body>
</html>
"""
    d = os.path.join(OUT, path)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(doc)

FOOT = f'<p class="foot">Music by Starrah Hazely Parsons · © 2026 I.Q. Productionz<br><a href="mailto:{EMAIL}">{EMAIL}</a></p>'
COVER = BASE + '/Assets/cover.jpg'

# ---------- Cover art: download any song's Spotify cover that isn't saved yet ----------
os.makedirs(os.path.join(OUT, 'Assets', 'Covers'), exist_ok=True)
for t, yt, sp, ln in SONGS:
    dest = os.path.join(OUT, 'Assets', 'Covers', f'{sp}.jpg')
    if os.path.exists(dest):
        continue   # WHY skip: covers never change, so only new songs hit the network
    try:
        # WHY oEmbed: Spotify's public endpoint returns the official square art, no login needed
        info = json.load(urllib.request.urlopen(
            f'https://open.spotify.com/oembed?url=https://open.spotify.com/track/{sp}', timeout=15))
        urllib.request.urlretrieve(info['thumbnail_url'], dest)
        print('downloaded cover for', t)
    except Exception as e:
        # WHY keep going: one bad ID shouldn't stop the other pages from building
        print('could not get cover for', t, '-', e)

# ---------- /Links/ : the main one-link page ----------
links_body = f"""<header class="top">
  {brand('../')}
  <h1 class="sr-only">New Thought Nursery links</h1>
  <p class="sub">{len(SONGS)} songs · nursery rhymes rewritten with safe, gentle scenarios</p>
</header>
<main class="band"><div class="col">
  <p class="eyebrow">Listen</p>
  {btn('../Music/', 'All Songs', 'list', 'hero', ext=False)}
  {btn(SPOTIFY_ARTIST, 'Spotify', 'spotify', 'spotify')}
  {btn(YTM_PLAYLIST, 'YouTube Music', 'ytmusic', 'ytm')}
  {btn(YT_PLAYLIST, 'YouTube Playlist', 'play', 'yt')}
  {btn(YT_CHANNEL, 'YouTube Channel', 'youtube', 'yt')}
  <p class="eyebrow">More</p>
  {btn('../#book', 'Row Row Ocean — picture book', 'book', ext=False)}
  {btn('../', 'Website', 'home', ext=False)}
  {btn('../Contact/', 'Contact &amp; bookings'.replace('&amp;', '&'), 'mail', ext=False)}
  {FOOT}
</div></main>"""
page('Links', 'New Thought Nursery | Links', 'Listen to New Thought Nursery on Spotify, YouTube and YouTube Music, plus the Row Row Ocean picture book.', COVER, links_body, 1)

# ---------- /Music/ : clickable song list ----------
music_css = """
.songs{list-style:none;margin:0;padding:0}
.songs a{display:flex;align-items:center;gap:.85rem;padding:.55rem .6rem;margin-bottom:.5rem;border-radius:.9rem;
  color:#fff;text-decoration:none;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);transition:background .15s ease}
.songs a:hover{background:rgba(255,255,255,.13)}
.songs a:focus-visible{outline:3px solid var(--card-mint);outline-offset:2px}
.songs img{width:52px;height:52px;border-radius:.55rem;object-fit:cover;flex:none;background:#3a3470}
.songs .t{flex:1;min-width:0;font-weight:700;line-height:1.25}
.songs .t small{display:block;font-weight:400;color:var(--card-blush);opacity:.8}
.songs .n{font:700 .8rem/1 var(--f-body);color:var(--card-mint);width:1.4rem;text-align:right;flex:none}
"""
rows = []
for i, (t, yt, sp, ln) in enumerate(SONGS, 1):
    rows.append(f'<li><a href="{slug(t)}/"><span class="n">{i}</span>'
                f'<img src="../Assets/Covers/{sp}.jpg" alt="" loading="lazy" width="52" height="52">'
                f'<span class="t">{E(short(t))}<small>{"Remix · " if "(Remix)" in t else ""}{ln}</small></span></a></li>')
music_body = f"""<header class="top">
  {brand('../')}
  <h1 class="name">The Music</h1>
  <p class="tag">Tap a song to listen anywhere</p>
  <a class="back" href="../Links/">← All links</a>
</header>
<main class="band"><div class="col">
  {btn(SPOTIFY_ARTIST, 'Play everything on Spotify', 'spotify', 'hero')}
  <p class="eyebrow">{len(SONGS)} songs</p>
  <ol class="songs">
  {''.join(rows)}
  </ol>
  {FOOT}
</div></main>"""
page('Music', 'New Thought Nursery | All Songs', f'All {len(SONGS)} New Thought Nursery songs. Tap any song for Spotify, YouTube and YouTube Music links.', COVER, music_body, 1, music_css)

# ---------- /Music/<Song>/ : one-link page per song ----------
song_css = """
.art{width:min(12rem,52vw);margin-top:1.25rem;aspect-ratio:1;border-radius:1.1rem;object-fit:cover;display:block;
  box-shadow:0 20px 40px -20px rgba(43,37,86,.6);background:#e9e4f7}
.top .name{margin-top:1rem}
.nav{display:flex;gap:.6rem;margin-top:1.25rem}
.nav a{flex:1;text-align:center;padding:.7rem .5rem;border-radius:999px;border:1px solid rgba(255,255,255,.25);
  color:#fff;text-decoration:none;font-weight:700;font-size:.9rem;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.nav a:hover{background:rgba(255,255,255,.1)}
.nav a:focus-visible{outline:3px solid var(--card-mint);outline-offset:2px}
"""
n = len(SONGS)
for i, (t, yt, sp, ln) in enumerate(SONGS):
    prev_t, nxt_t = SONGS[(i - 1) % n][0], SONGS[(i + 1) % n][0]   # WHY wrap: last song loops to first
    thumb = f'../../Assets/Covers/{sp}.jpg'   # WHY local square art: YouTube thumbs are letterboxed
    body = f"""<header class="top">
  {brand('../../')}
  <img class="art" src="{thumb}" alt="{E(short(t))} cover art" width="240" height="240">
  <h1 class="name">{E(short(t))}</h1>
  <p class="sub">New Thought Nursery{" · Remix" if "(Remix)" in t else ""} · {ln}</p>
  <a class="back" href="../">← All songs</a>
</header>
<main class="band"><div class="col">
  <p class="eyebrow">Listen on</p>
  {btn(f'https://open.spotify.com/track/{sp}', 'Spotify', 'spotify', 'hero')}
  {btn(f'https://www.youtube.com/watch?v={yt}', 'YouTube', 'youtube', 'yt')}
  {btn(f'https://music.youtube.com/watch?v={yt}', 'YouTube Music', 'ytmusic', 'ytm')}
  <div class="nav">
    <a href="../{slug(prev_t)}/" aria-label="Previous song: {E(short(prev_t))}">← {E(short(prev_t))}</a>
    <a href="../{slug(nxt_t)}/" aria-label="Next song: {E(short(nxt_t))}">{E(short(nxt_t))} →</a>
  </div>
  {FOOT}
</div></main>"""
    page(f'Music/{slug(t)}', f'{short(t)} | New Thought Nursery',
         f'Listen to "{t}" by New Thought Nursery on Spotify, YouTube and YouTube Music.',
         f'{BASE}/Assets/Covers/{sp}.jpg', body, 2, song_css)

# ---------- sitemap: add the new pages ----------
sm = os.path.join(OUT, 'sitemap.xml')
if os.path.exists(sm):
    s = open(sm, encoding='utf-8').read()
    new = ['Links/', 'Music/'] + [f'Music/{slug(t)}/' for t, *_ in SONGS]
    add = ''.join(f'  <url><loc>{BASE}/{p}</loc><lastmod>2026-10-24</lastmod></url>\n'
                  for p in new if f'{BASE}/{p}<' not in s)
    s = s.replace('</urlset>', add + '</urlset>')
    open(sm, 'w', encoding='utf-8').write(s)

print('built', 2 + n, 'pages; slugs:', [slug(t) for t, *_ in SONGS])
