// Rain Drop website: the sign-up box, the postcode box and the example video.

const signup = document.getElementById("signup");
const form = document.getElementById("signup-form");
const error = document.getElementById("signup-error");
const thanks = document.getElementById("signup-thanks");

document.querySelectorAll("[data-open-signup]").forEach((b) => b.addEventListener("click", () => signup.showModal()));
document.querySelectorAll("[data-close-signup]").forEach((b) => b.addEventListener("click", () => signup.close()));
signup.addEventListener("click", (e) => { if (e.target === signup) signup.close(); }); // a click on the faded page

const number = (input) => (input.value.trim() === "" ? null : Number(input.value.trim()));

function problem(f) {
  if (!f.farm_name.value.trim()) return "Please enter your farm's name.";
  if (!f.email.validity.valid || !f.email.value.trim()) return "Please enter a valid email address.";
  const lat = number(f.lat), lon = number(f.lon), address = f.address.value.trim();
  const hasPoint = lat !== null || lon !== null;
  if (!hasPoint && !address) return "Please enter your farm's Lat and Lon, or its address.";
  if (hasPoint && !address) {
    if (lat === null || lon === null) return "Please enter both Lat and Lon.";
    // Eastern Australia, roughly: the forecasts cover VIC, NSW, QLD and SA
    if (!(lat >= -44 && lat <= -10) || !(lon >= 129 && lon <= 154)) {
      return "That Lat and Lon isn't in eastern Australia. Lat is negative, e.g. -38.46, and Lon e.g. 144.91.";
    }
  }
  return "";
}

// Sign-ups go to raindrop@odsl.co by email through Web3Forms (the user's choice, 13 Nov 2026). The access key only
// lets anyone send to that one address, and Web3Forms says it is safe in public pages.
const WEB3FORMS_KEY = "";  // from web3forms.com for raindrop@odsl.co
const enter = form.querySelector(".button--enter");
const FAILED = 'Sorry, that didn\'t go through. Please try again, or email <a href="mailto:raindrop@odsl.co">raindrop@odsl.co</a>.';

async function send(f) {
  const fields = Object.fromEntries(new FormData(f));  // farm_name, email, lat, lon, address (+ botcheck if a bot ticked it)
  const response = await fetch("https://api.web3forms.com/submit", {
    method: "POST",
    headers: {"Content-Type": "application/json", Accept: "application/json"},
    body: JSON.stringify({
      ...fields,
      access_key: WEB3FORMS_KEY,
      subject: `Rain Drop sign-up: ${fields.farm_name.trim()}`,
      from_name: "Rain Drop website",
      replyto: fields.email.trim(),
    }),
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.success) throw new Error(result.message || `HTTP ${response.status}`);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = problem(form);
  error.textContent = message;
  if (message) return;
  if (!WEB3FORMS_KEY) {  // until the key is in: point people to the inbox instead
    error.innerHTML = 'Online sign-up opens shortly. For now, please email your farm\'s name and location to '
      + '<a href="mailto:raindrop@odsl.co?subject=Rain%20Drop%20sign-up">raindrop@odsl.co</a>.';
    return;
  }
  enter.disabled = true;
  enter.textContent = "Sending…";
  try {
    await send(form);
  } catch (err) {
    console.warn("sign-up not sent:", err);
    error.innerHTML = FAILED;
    enter.disabled = false;
    enter.textContent = "Enter";
    return;
  }
  form.querySelectorAll(".field, .field-row, .or, .button--enter, .privacy").forEach((el) => (el.hidden = true));
  thanks.textContent = `Thanks, ${form.farm_name.value.trim()}. We'll be in touch to set up your first forecast.`;
  thanks.hidden = false;
});

// "How much better will it be for me?": the postcode's nearest tested town (data/postcodes.js, built by
// tools/build_postcodes.py) and how much more accurate our chance of rain was there than a typical single model.
const DATA = window.RAIN_DROP_DATA;
const postcodeForm = document.getElementById("postcode-form");
const result = document.getElementById("postcode-result");
const note = document.getElementById("postcode-note");
const SAME = 2; // under 2% either way reads as "about as accurate"

function better(pct, days) {
  return pct >= SAME ? `<strong>${pct}% more accurate</strong> ${days}` : `about as accurate ${days}`;
}

function answer(code) {
  if (!/^\d{4}$/.test(code)) return "Please enter a 4-digit postcode.";
  const hit = DATA.postcodes[code];
  if (!hit) return `We couldn't find postcode ${code}.`;
  if (hit[0] < 0) return "We don't forecast in Western Australia, Tasmania or the Northern Territory yet.";
  const [name, state, d13, d47] = DATA.towns[hit[0]];
  const km = hit[1] < 1 ? "less than 1 km away" : `${hit[1]} km away`;
  let text = `Your nearest tested town is <strong>${name}, ${state}</strong> (${km}). There, our chance of rain was `
    + `${better(d13, "over the next three days")} than a typical single weather model, and `
    + `${better(d47, "for days 4–7")}.`;
  if (hit[1] > 150) text += " That's a long way from you, so treat it as a rough guide.";
  return text;
}

postcodeForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const code = document.getElementById("postcode").value.trim();
  const text = answer(code);
  result.innerHTML = text; // built only from our own data and a checked 4-digit code
  const found = text.startsWith("Your nearest");
  // Bracken Ridge, days 1-3, out of sample: the gauge-tuned chance vs the email, about 11-13% (farm-rain-forecast
  // research/farm_tuning/); one farm so far, hence "likely"
  document.getElementById("postcode-gauge").hidden = !found;
  note.hidden = !found;
  note.textContent = found ? `Measured ${DATA.period} against recorded rain (SILO). A typical single model is the average `
    + "of the seven weather models we combine. Postcode locations: GeoNames (CC BY 4.0)." : "";
});

// The three box titles stay on one line: 22 px as designed, all shrunk together only when a column is too narrow
const titles = [...document.querySelectorAll(".card-title")];
function fitTitles() {
  titles.forEach((t) => (t.style.fontSize = ""));
  const ratio = Math.min(...titles.map((t) => t.clientWidth / t.scrollWidth));
  if (ratio < 1) titles.forEach((t) => (t.style.fontSize = `${Math.floor(22 * ratio * 10) / 10}px`));
}
new ResizeObserver(fitTitles).observe(document.querySelector(".cards"));
document.fonts.ready.then(fitTitles);

// The example video doesn't play for people who ask their device for less motion
const video = document.getElementById("example-video");
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  video.removeAttribute("autoplay");
  video.pause();
}

// A link ending in #signup (e.g. from an email) opens the sign-up box straight away
if (location.hash === "#signup") signup.showModal();
