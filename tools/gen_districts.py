#!/usr/bin/env python3
"""
Rebuild the crawlable layer of studenttrustee.net.

The roster already lives in map.html, inside the page, where only a browser
running JavaScript can see it. Search engines cannot, which is why a student
googling "Cabrillo student trustee" never lands here. This writes one static
page per district from that same roster, plus the index, sitemap and robots
file that let them be found.

Single source of truth: the DATA object in studenttrustee/map.html. Re-run this
whenever the roster is updated and every page below regenerates in step.

    python3 tools/gen_districts.py

Writes into studenttrustee/districts/, plus sitemap.xml and robots.txt.
"""
import json
import os
import re
import sys
import unicodedata
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'studenttrustee')
MAP = os.path.join(SITE, 'map.html')
OUT = os.path.join(SITE, 'districts')

ORIGIN = 'https://studenttrustee.net'
LAST_VERIFIED = '2026-09-22'      # keep in step with index.html

REGIONS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
REGION_NAME = {
    'I': 'Far North', 'II': 'Sacramento & North Valley', 'III': 'East & North Bay',
    'IV': 'South Bay & Central Coast', 'V': 'Central Valley', 'VI': 'South Central Coast',
    'VII': 'Los Angeles', 'VIII': 'Orange County & San Gabriel',
    'IX': 'Inland Empire & Desert', 'X': 'San Diego & Imperial',
}
REGION_HEX = {
    'I': '#eda100', 'II': '#4a3aa7', 'III': '#1baf7a', 'IV': '#9c27b0', 'V': '#008300',
    'VI': '#e87ba4', 'VII': '#2a78d6', 'VIII': '#eb6834', 'IX': '#0e8fae', 'X': '#e34948',
}


def slug(s):
    """Byte-for-byte the same slug map.html uses, so #d= deep links still match."""
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def load_districts():
    with open(MAP, encoding='utf-8') as fh:
        src = fh.read()
    m = re.search(r'^const DATA = (\{.*\});\s*$', src, re.M)
    if not m:
        sys.exit('could not find the DATA object in map.html')
    data = json.loads(m.group(1))
    return data['districts']


# ---------------------------------------------------------------- page chrome

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{origin}/brand/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/brand/poppy-p6.ico" sizes="48x48">
<link rel="icon" href="/brand/poppy-p6.svg" sizes="any" type="image/svg+xml">
<link rel="apple-touch-icon" sizes="180x180" href="/brand/poppy-180-p6.png">
<link rel="mask-icon" href="/brand/poppy-mask-p6.svg" color="#CC480D">
<link rel="manifest" href="/site-p6.webmanifest">
<style>
  :root{{
    --surface-1:#ffffff; --plane:#f6f6f6;
    --text-primary:#0a0a0a; --text-secondary:#4a4a4a; --text-muted:#8a8a8a;
    --rule:#e3e3e3;
  }}
  *{{box-sizing:border-box}}
  html,body{{margin:0}}
  body{{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--plane);
    color:var(--text-primary);-webkit-font-smoothing:antialiased;line-height:1.5}}
  a{{color:inherit}}
  .top{{display:flex;align-items:center;gap:14px;padding:14px 24px;flex-wrap:wrap;
    border-top:2px solid var(--text-primary);background:var(--surface-1);
    border-bottom:1px solid var(--rule)}}
  .mark img{{display:block;height:22px;width:auto}}
  .grow{{flex:1}}
  .top nav{{display:flex;flex-wrap:wrap;gap:6px}}
  .top nav a{{font-size:12.5px;color:var(--text-secondary);text-decoration:none;
    border:1px solid var(--rule);padding:6px 11px;background:var(--surface-1);display:inline-block}}
  .top nav a:hover{{color:var(--text-primary);border-color:var(--text-primary)}}
  main{{max-width:1080px;margin:0 auto;padding:44px 24px 0}}
  .crumb{{font-size:11px;text-transform:uppercase;letter-spacing:.13em;font-weight:650;
    color:var(--text-muted);margin:0 0 26px}}
  .crumb a{{text-decoration:none}}
  .crumb a:hover{{text-decoration:underline;text-underline-offset:3px}}
  .eyebrow{{display:flex;align-items:center;gap:8px;font-size:10px;text-transform:uppercase;
    letter-spacing:.13em;font-weight:650;color:var(--text-muted);margin:0 0 12px}}
  .sw{{width:9px;height:9px;flex:none;display:inline-block}}
  h1{{font-size:46px;line-height:1.06;letter-spacing:-.042em;font-weight:680;margin:0 0 18px;
    max-width:18ch}}
  .cols{{font-size:17px;color:var(--text-secondary);max-width:58ch;margin:0 0 34px;line-height:1.55}}
  h2{{font-size:10px;text-transform:uppercase;letter-spacing:.13em;font-weight:650;
    color:var(--text-muted);margin:0;padding:0 0 14px}}
  .rows{{border-top:1px solid var(--rule);margin:0 0 34px}}
  .row{{border-bottom:1px solid var(--rule);padding:18px 0}}
  .row .n{{font-size:20px;letter-spacing:-.018em;font-weight:660;margin:0 0 6px}}
  .row dl{{display:grid;grid-template-columns:82px 1fr;gap:4px 16px;margin:0;
    font-size:13.5px;color:var(--text-secondary)}}
  .row dt{{font-size:10px;text-transform:uppercase;letter-spacing:.13em;font-weight:650;
    color:var(--text-muted);padding-top:3px}}
  .row dd{{margin:0;overflow-wrap:anywhere}}
  .row dd a{{text-decoration:underline;text-underline-offset:3px}}
  .unk{{color:var(--text-muted)}}
  .none{{border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);
    padding:18px 0;margin:0 0 34px;font-size:14px;color:var(--text-secondary)}}
  .out{{border-top:1px solid var(--rule)}}
  .out a{{display:block;border-bottom:1px solid var(--rule);padding:16px 0;text-decoration:none;
    font-size:15px;font-weight:600}}
  .out a:hover span{{text-decoration:underline;text-underline-offset:3px}}
  .out .k{{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.13em;
    font-weight:650;color:var(--text-muted);margin-bottom:5px}}
  .sibs{{display:flex;justify-content:space-between;gap:20px;margin:40px 0 0;
    border-top:1px solid var(--rule);padding-top:18px;font-size:13px}}
  .sibs a{{text-decoration:none;color:var(--text-secondary);max-width:46%}}
  .sibs a:hover{{color:var(--text-primary);text-decoration:underline;text-underline-offset:3px}}
  .sibs .r{{text-align:right}}
  .grp{{margin:0 0 6px;border-top:1px solid var(--rule)}}
  .grp h2{{padding:20px 0 10px;display:flex;align-items:center;gap:8px}}
  .grp ul{{list-style:none;margin:0;padding:0}}
  .grp li{{border-top:1px solid var(--rule)}}
  .grp li a{{display:flex;justify-content:space-between;gap:20px;padding:14px 0;
    text-decoration:none;font-size:15px}}
  .grp li a:hover .t{{text-decoration:underline;text-underline-offset:3px}}
  .grp .who{{font-size:13px;color:var(--text-muted);text-align:right;flex:none;max-width:48%}}
  footer{{border-top:1px solid var(--rule);margin-top:60px;padding:20px 24px 50px;
    font-size:11.5px;color:var(--text-muted);max-width:1080px;margin-left:auto;margin-right:auto}}
  footer a{{text-decoration:underline;text-underline-offset:2px}}
  @media(max-width:880px){{h1{{font-size:34px}}
    .row dl{{grid-template-columns:1fr;gap:2px}}
    .row dt{{padding-top:8px}}
    .grp li a{{display:block}}.grp .who{{text-align:left;max-width:none;margin-top:3px}}
    .sibs{{display:block}}.sibs .r{{text-align:left;margin-top:12px}}}}
</style>
</head>
<body>
<header class="top">
  <div class="mark"><a href="/"><img src="/brand/logo-wordmark.png" alt="StudentTrustee.net" width="1015" height="127"></a></div>
  <div class="grow"></div>
  <nav>
    <a href="/">Home</a><a href="/map">District map</a><a href="/districts/"{here}>Districts</a><a href="/legislature">Legislature</a><a href="/about">About</a>
  </nav>
</header>
<main>
"""

FOOT = """</main>
<footer>Maintained by Nick Bonasera, Student Trustee, Contra Costa Community College District.
Roster verified {stamp}. For site corrections,
<a href="mailto:studenttrustee@4cd.edu?subject=Student%20Trustee%20Website%20Update">please reach out</a>
with updated information.</footer>
</body>
</html>
"""


def stamp(iso):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    y, m, d = (int(x) for x in iso.split('-'))
    return '%d %s %d' % (d, months[m - 1], y)


def page(title, desc, canon, body, here=False):
    return (HEAD.format(title=esc(title), desc=esc(desc), canon=canon,
                        origin=ORIGIN, here=' aria-current="page"' if here else '')
            + body + FOOT.format(stamp=stamp(LAST_VERIFIED)))


# ------------------------------------------------------------- district pages

def district_body(d, prev, nxt):
    sg = slug(d['name'])
    hex_ = REGION_HEX[d['region']]
    out = []
    out.append('<p class="crumb"><a href="/">Home</a> &rsaquo; '
               '<a href="/districts/">Districts</a> &rsaquo; %s</p>' % esc(d['name']))
    out.append('<p class="eyebrow"><span class="sw" style="background:%s"></span>'
               'Region %s &middot; %s</p>'
               % (hex_, esc(d['region']), esc(REGION_NAME[d['region']])))
    out.append('<h1>%s</h1>' % esc(d['name']))
    out.append('<p class="cols">%s</p>' % ' &middot; '.join(esc(c) for c in d['colleges']))

    people = d.get('trustees') or []
    if people:
        label = 'Student trustee' if len(people) == 1 else 'Student trustees'
        out.append('<h2>%s</h2>' % label)
        out.append('<div class="rows">')
        for p in people:
            rows = []
            if p.get('email'):
                rows.append('<dt>Email</dt><dd><a href="mailto:%s">%s</a></dd>'
                            % (esc(p['email']), esc(p['email'])))
            else:
                rows.append('<dt>Email</dt><dd class="unk">Not listed yet</dd>')
            rows.append('<dt>District</dt><dd>%s</dd>' % esc(d['name']))
            if p.get('college'):
                rows.append('<dt>College</dt><dd>%s</dd>' % esc(p['college']))
            out.append('<div class="row"><p class="n">%s %s</p><dl>%s</dl></div>'
                       % (esc(p['first']), esc(p['last']), ''.join(rows)))
        out.append('</div>')
    elif d.get('seat') == 'vacant':
        src = ''
        if d.get('seatSource'):
            src = (' <a href="%s" target="_blank" rel="noopener">Board page &#8599;</a>'
                   % esc(d['seatSource']))
        out.append('<p class="none">The district lists this seat as vacant.%s</p>' % src)
    else:
        out.append('<p class="none">No student trustee is listed for this district in the '
                   'current roster. If the seat is filled, the district board page below is '
                   'the place to check.</p>')

    out.append('<h2>Where to go next</h2>')
    out.append('<div class="out">')
    out.append('<a href="/map#d=%s"><span class="k">Map</span>'
               '<span>See this district on the map</span></a>' % esc(sg))
    if d.get('web'):
        out.append('<a href="%s" target="_blank" rel="noopener"><span class="k">District</span>'
                   '<span>District website &#8599;</span></a>' % esc(d['web']))
    if d.get('board'):
        out.append('<a href="%s" target="_blank" rel="noopener"><span class="k">Governance</span>'
                   '<span>Board of Trustees &#8599;</span></a>' % esc(d['board']))
    out.append('</div>')

    sibs = []
    if prev:
        sibs.append('<a href="/districts/%s/">&larr; %s</a>' % (slug(prev['name']), esc(prev['name'])))
    else:
        sibs.append('<span></span>')
    if nxt:
        sibs.append('<a class="r" href="/districts/%s/">%s &rarr;</a>' % (slug(nxt['name']), esc(nxt['name'])))
    out.append('<div class="sibs">%s</div>' % ''.join(sibs))

    out.append(json_ld(d))
    return '\n'.join(out) + '\n'


def json_ld(d):
    sg = slug(d['name'])
    node = {
        '@context': 'https://schema.org',
        '@type': 'GovernmentOrganization',
        'name': d['name'],
        'url': '%s/districts/%s/' % (ORIGIN, sg),
        'areaServed': {'@type': 'AdministrativeArea',
                       'name': 'Region %s, California Community Colleges' % d['region']},
        'address': {'@type': 'PostalAddress', 'addressRegion': 'CA', 'addressCountry': 'US'},
    }
    if d.get('web'):
        node['sameAs'] = [d['web']]
    if d.get('colleges'):
        node['subOrganization'] = [{'@type': 'CollegeOrUniversity', 'name': c}
                                   for c in d['colleges']]
    members = []
    for p in d.get('trustees') or []:
        m = {'@type': 'Person', 'name': ('%s %s' % (p['first'], p['last'])).strip(),
             'jobTitle': 'Student Trustee'}
        if p.get('email'):
            m['email'] = p['email']
        members.append({'@type': 'OrganizationRole', 'roleName': 'Student Trustee', 'member': m})
    if members:
        node['member'] = members
    return ('<script type="application/ld+json">%s</script>'
            % json.dumps(node, ensure_ascii=False, separators=(',', ':')))


# --------------------------------------------------------------- index page

def index_body(ds):
    out = []
    out.append('<p class="crumb"><a href="/">Home</a> &rsaquo; Districts</p>')
    out.append('<h1>All 72 districts.</h1>')
    out.append('<p class="cols">Every California community college district, grouped by the ten '
               'regions the Community College League uses, with the student trustee who holds each '
               'board seat. Each district has its own page.</p>')
    for r in REGIONS:
        grp = [d for d in ds if d['region'] == r]
        if not grp:
            continue
        out.append('<div class="grp">')
        out.append('<h2><span class="sw" style="background:%s"></span>Region %s &middot; %s '
                   '&middot; %d districts</h2>'
                   % (REGION_HEX[r], esc(r), esc(REGION_NAME[r]), len(grp)))
        out.append('<ul>')
        for d in grp:
            people = d.get('trustees') or []
            if people:
                who = ', '.join(('%s %s' % (p['first'], p['last'])).strip() for p in people)
            elif d.get('seat') == 'vacant':
                who = 'Seat vacant'
            else:
                who = 'Not listed'
            out.append('<li><a href="/districts/%s/"><span class="t">%s</span>'
                       '<span class="who">%s</span></a></li>'
                       % (slug(d['name']), esc(d['name']), esc(who)))
        out.append('</ul></div>')
    return '\n'.join(out) + '\n'


# ------------------------------------------------------------------ sitemap

def write_sitemap(ds):
    today = date.today().isoformat()
    urls = [('/', '1.0'), ('/map', '0.9'), ('/districts/', '0.9'),
            ('/legislature', '0.7'), ('/about', '0.6')]
    urls += [('/districts/%s/' % slug(d['name']), '0.8') for d in ds]
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, pri in urls:
        body.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod>'
                    '<priority>%s</priority></url>' % (ORIGIN, path, today, pri))
    body.append('</urlset>')
    with open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(body) + '\n')
    return len(urls)


def write_robots():
    txt = ('User-agent: *\n'
           'Allow: /\n'
           '\n'
           'Sitemap: %s/sitemap.xml\n' % ORIGIN)
    with open(os.path.join(SITE, 'robots.txt'), 'w', encoding='utf-8') as fh:
        fh.write(txt)


# ---------------------------------------------------------------------- main

def main():
    ds = sorted(load_districts(), key=lambda d: d['name'])
    seen = {}
    for d in ds:
        sg = slug(d['name'])
        if sg in seen:
            sys.exit('slug collision: %r and %r both give %r' % (seen[sg], d['name'], sg))
        seen[sg] = d['name']

    os.makedirs(OUT, exist_ok=True)
    for i, d in enumerate(ds):
        sg = slug(d['name'])
        people = d.get('trustees') or []
        if people:
            who = ' and '.join(('%s %s' % (p['first'], p['last'])).strip() for p in people)
            desc = ('%s is the student trustee for %s. Contact details, the colleges in the '
                    'district, and the board page.' % (who, d['name'])) if len(people) == 1 else \
                   ('%s are the student trustees for %s. Contact details, the colleges in the '
                    'district, and the board page.' % (who, d['name']))
        else:
            desc = ('%s has no student trustee listed in the current roster. The colleges in '
                    'the district and its board page.' % d['name'])
        title = '%s Student Trustee | studenttrustee.net' % d['name']
        canon = '%s/districts/%s/' % (ORIGIN, sg)
        html = page(title, desc, canon,
                    district_body(d, ds[i - 1] if i else None,
                                  ds[i + 1] if i + 1 < len(ds) else None))
        folder = os.path.join(OUT, sg)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8') as fh:
            fh.write(html)

    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(page('All 72 California Community College Districts | studenttrustee.net',
                      'Every California community college district and its student trustee, '
                      'grouped by region. One page per district.',
                      '%s/districts/' % ORIGIN, index_body(ds), here=True))

    n = write_sitemap(ds)
    write_robots()
    trustees = sum(len(d.get('trustees') or []) for d in ds)
    print('%d district pages + index' % len(ds))
    print('%d trustees carried over' % trustees)
    print('sitemap.xml: %d urls' % n)
    print('robots.txt written')


if __name__ == '__main__':
    main()
