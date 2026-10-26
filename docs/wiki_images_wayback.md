# Wiki images / Wayback attempt (Step 9.1)

## State

`data/wiki/image_index.json`: 698 images present, 209 errors (403/no URL),
34 priority images still blocked. Existing files remain in `archive/wiki/raw`.

## Attempts (2026-10-26)

1. Direct Fandom `Special:FilePath` URLs: **403 Forbidden** (previous runs).
2. Wayback `https://web.archive.org/web/2023id_/https://transformers-forged-to-fight.fandom.com/wiki/Special:FilePath/<file>`:
   **404 NOT FOUND** for `Act_1.jpg`, `Arcee_portrait.png`,
   `Alliance_Icon.png`.
3. Wayback CDX API wildcard query: **503 Service Unavailable**.

No image was downloaded; `work/wayback/` is empty. This is the third
experimental attempt, so per the queue rule the item is stopped and recorded.

## Why it fails

The index has only filenames, not the Fandom `static.wikia.nocookie.net` hash
path. `Special:FilePath` is not archived by Wayback for this wiki, and the
direct wiki returns 403 without a browser session/Referer. A CDX query is the
right way to find archived `static.wikia` URLs, but the API returned 503 at
the time of the attempt.

## What is needed

- A list of exact `static.wikia.nocookie.net/.../revision/latest` URLs, or
- a browser session/export with the images, or
- a later Wayback retry when the CDX API is available (polite, 1–2 s pauses).

Do not hammer the wiki; do not add binary images to git. `docs/screens_ok/` is
the only tracked image exception.
