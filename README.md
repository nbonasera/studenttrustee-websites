# studenttrustee.net

Two static sites, one repo. No build step: what is in each folder is what gets
served, so anything you can open in a browser locally is exactly what ships.

```
studenttrustee/ -> studenttrustee.net
volunteer/      -> volunteer.studenttrustee.net
```

## Deploying

Each folder is its own Netlify site. In Netlify, for each one:

| Setting           | studenttrustee.net | volunteer.studenttrustee.net |
|-------------------|--------------------|------------------------------|
| Base directory    | `studenttrustee`   | `volunteer`                  |
| Build command     | *(leave empty)*    | *(leave empty)*              |
| Publish directory | `studenttrustee`   | `volunteer`                  |

Once both are pointed at this repo, pushing to `main` deploys. No more
drag-and-drop, and no more losing files to a bad upload.

## What is here

**studenttrustee/** — landing page, the 72-district map, legislative calendars, about.
`map.html` carries the district polygons and pulls boundaries from the
Foundation for California Community Colleges GIS service at runtime. The
basemap is Esri Light Gray Canvas; it was CARTO until CARTO started requiring
an API key and stamping unkeyed tiles with a watermark.

**volunteer/** — the Bay Area volunteer directory. `data.js` holds all 262
organizations; `index.html` is the whole interface.

**brand/** — shared identity. The poppy mark, the wordmark, the favicon set.
`poppy-p6.svg` is true vector; the PNGs and the `.ico` are rasters of the same
artwork. The `-p6` suffix is a cache-busting version: Safari keys its favicon
cache on the URL path, so changing an icon means changing its filename, not
just adding a query string.

## Known gaps

These are missing and known, not forgotten:

- **`_headers` is absent from both sites.** Netlify consumes it at build time
  and never serves it back, so the original could not be recovered. If you
  still have it, drop it in the relevant folder.
- **The volunteer PDFs are not committed.** `bay-area-volunteer-directory.pdf`
  and `bay-area-volunteer-how-to-apply.pdf` are linked from `volunteer/` and
  will 404 until added.
- **The 72 per-district pages, `sitemap.xml` and `robots.txt` are gone.** A
  deploy dropped them and no backup survived; the files that looked like
  backups turned out to be saved copies of Netlify's 404 page. They need
  regenerating from the roster data. Until then Google can only see four pages
  of the main site.

## Roster freshness

The roster was last fully checked 2 July 2026, with corrections through
22 September 2026. Four districts remain unverified because their board
systems block crawlers: Feather River, Solano, Monterey Peninsula, Compton.
