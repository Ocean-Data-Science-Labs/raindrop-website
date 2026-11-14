# Rain Drop website

The site for [raindrop.odsl.co](https://raindrop.odsl.co): static pages (HTML, CSS and a little JavaScript, no build
step), served by GitHub Pages from `main`. Designed in Figma (file RAIN DROP, page "Website").

- **Sign-up:** a dialog that opens from either "Sign up here" button, or from a link ending in `#signup`. It sends each
  sign-up by email to raindrop@odsl.co through [Web3Forms](https://web3forms.com): put the access key in
  `WEB3FORMS_KEY` in `script.js`. The key is public by design and can only send to that address. A hidden `botcheck`
  box catches spam bots. The free plan only takes submissions from a browser, and its Cloudflare
  blocks headless browsers too, so test it by hand in a normal browser on the live page.
- **Address finder:** the sign-up's Farm Address box suggests Australian addresses as people type (Mapbox Address
  Autofill API, `MAPBOX_TOKEN` in `script.js`). Choosing one fills Lat and Lon, so sign-ups arrive with coordinates.
  The token is public and only works on raindrop.odsl.co (a URL restriction in the Mapbox account), so test it on
  the live page. It's our own small list, not Mapbox's widget, because that widget puts its list outside the open
  sign-up box, where the box hides it. Billing is per session (1,000 free a month): searches wait for 3 characters
  and a short pause, and choosing an address ends the session. An address typed in full without choosing still works.
- **"How much better will it be for me?":** `data/postcodes.js` maps each postcode (GeoNames, CC BY 4.0) to the nearest
  of 151 tested towns. For each town it gives how much more accurate Rain Drop's chance of 1 mm+ rain was than a typical
  single weather model (the average Brier score of the 7 ensemble models), days 1-3 and 4-7, Jan to Nov 2026, scored
  against SILO. It is built by `tools/build_postcodes.py` from the (private) forecast repo's archive.
- **Example forecast:** `assets/example-forecast.mp4`, the Mornington chart scrolling (`tools/make_forecast_video.py`).
- **Header:** sits on the page's white cloud edge (`assets/cloud-*.svg`, `tools/make_cloud_edges.py`), drifting slowly.
  There's no drifting, autoplaying video or button animation for visitors who ask their device for less motion.
- **Fonts:** ABC Areal / ABC Areal Semi Mono where installed, otherwise IBM Plex Sans / Plex Mono (Google Fonts). The
  logo's wordmark is outlined in `assets/logo-lockup.svg`.

To preview, open `index.html` in a browser.
