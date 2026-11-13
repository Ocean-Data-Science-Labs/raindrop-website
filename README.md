# Rain Drop website

The site for [raindrop.odsl.co](https://raindrop.odsl.co): static pages (HTML, CSS and a little JavaScript, no build
step), served by GitHub Pages from `main`. Designed in Figma (file RAIN DROP, page "Website").

- **Sign-up:** a dialog that opens from either "Sign up here" button, or from a link ending in `#signup`. It sends each
  sign-up by email to raindrop@odsl.co through [Web3Forms](https://web3forms.com): put the access key in
  `WEB3FORMS_KEY` in `script.js`. The key is public by design and can only send to that address. A hidden `botcheck`
  box catches spam bots.
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
