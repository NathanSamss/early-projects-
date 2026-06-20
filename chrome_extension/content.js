// content.js
// Two-layer answer engine: Layer 1 template matching, Layer 2 supervised inference.
// CAPTCHA is never bypassed — the extension fills around it.

const SUBMIT_SELECTORS = [
  "button[type=submit]", "input[type=submit]",
  "button.template-btn-submit", "button.postings-btn",
];

function detectPlatform() {
  const u = location.href.toLowerCase();
  if (u.includes("jobs.lever.co"))     return "lever";
  if (u.includes("greenhouse.io"))     return "greenhouse";
  if (u.includes("ashbyhq.com"))       return "ashby";
  if (u.includes("myworkdayjobs.com") || u.includes("workday.com")) return "workday";
  return "unknown";
}

function isVisible(el) {
  if (!el) return false;
  const rect = el.getBoundingClientRect();
  if (rect.width < 10 || rect.height < 10) return false;
  const style = window.getComputedStyle(el);
  if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") return false;
  return true;
}

function detectCaptcha() {
  // Only flag a CAPTCHA when there is a VISIBLE challenge on the page.
  // Hidden reCAPTCHA elements that only activate on submit are ignored.
  const t = (document.body.innerText || "").toLowerCase();
  const text = ["click on the icons that are identical", "click on the icons that are",
    "select all images", "select all squares"];
  if (text.some(s => t.includes(s))) return true;

  const challengeSelectors = ["iframe[src*='recaptcha/api2/bframe']",
    "iframe[title*='recaptcha challenge']", "iframe[src*='hcaptcha'][title*='challenge']",
    ".challenge-container"];
  for (const sel of challengeSelectors) {
    try {
      const el = document.querySelector(sel);
      if (el && isVisible(el)) return true;
    } catch {}
  }
  return false;
}

const delay = (min, max) => new Promise(r => setTimeout(r, Math.random() * (max - min) + min));

async function typeInto(el, value) {
  el.focus();
  await delay(60, 160);
  el.value = "";
  el.dispatchEvent(new Event("input", { bubbles: true }));
  for (const ch of value) {
    el.value += ch;
    el.dispatchEvent(new Event("input", { bubbles: true }));
    await delay(12, 45);
  }
  el.dispatchEvent(new Event("change", { bubbles: true }));
  el.blur();
}

const TEMPLATE = [
  { key: "work_authorization",
    patterns: ["authorized to work", "work authorization", "legally authorized",
               "eligible to work", "require sponsorship", "need sponsorship",
               "require a visa", "visa sponsorship", "right to work"] },
  { key: "visa_type",
    patterns: ["what visa", "which visa", "visa are you on", "visa status", "type of visa"] },
  { key: "availability",
    patterns: ["notice period", "start date", "when can you start", "availability",
               "available to start", "ideal start"] },
  { key: "salary_expectation",
    patterns: ["salary", "compensation", "expected pay", "pay expectation",
               "rate expectation", "desired salary", "salary range"] },
  { key: "preferred_language",
    patterns: ["coding language", "programming language", "preferred language",
               "python or r", "preferred coding"] },
  { key: "relocate",
    patterns: ["relocate", "relocation", "willing to work", "on-site", "onsite",
               "work out of", "office 3x", "in office", "commute", "work from office"] },
  { key: "years_experience",
    patterns: ["years of experience", "years experience", "how many years", "year of experience"] },
  { key: "how_heard",
    patterns: ["how did you hear", "where did you hear", "how were you referred",
               "how you heard", "hear about"] },
  { key: "dei_gender",    patterns: ["gender"] },
  { key: "dei_ethnicity", patterns: ["ethnicity", "race"] },
  { key: "dei_age",       patterns: ["age bracket", "age range", "age group"] },
];

const CONSENT_PATTERNS = ["i consent", "consent to", "retaining my data",
                          "data retention", "privacy policy", "i agree"];

function cleanLabel(text) {
  if (!text) return "";
  return text.replace(/\s+/g, " ").trim();
}

// Collect candidate "question" texts once per fill: short, visible, text-bearing
// elements that could be a field label. Cached per run for performance.
let _labelCandidates = null;
function buildLabelCandidates() {
  const candidates = [];
  const selectors = "label, legend, .text, .application-label, h2, h3, h4, p, span, div";
  for (const el of document.querySelectorAll(selectors)) {
    // skip elements that contain form controls (they're containers, not labels)
    if (el.querySelector("input, select, textarea")) continue;
    const text = cleanLabel(el.textContent);
    if (!text || text.length < 3 || text.length > 220) continue;
    const rect = el.getBoundingClientRect();
    if (rect.width < 2 || rect.height < 2) continue;
    candidates.push({ text, top: rect.top, left: rect.left, bottom: rect.bottom, right: rect.right });
  }
  return candidates;
}

// Find the label for a control by spatial proximity: the nearest text that sits
// above, or to the left of, the control. Works regardless of DOM structure —
// this is the general solution that survives different site layouts.
function labelByProximity(el) {
  const r = el.getBoundingClientRect();
  if (r.width < 1 && r.height < 1) return "";
  if (!_labelCandidates) _labelCandidates = buildLabelCandidates();

  let best = "", bestDist = Infinity;
  for (const c of _labelCandidates) {
    // candidate must be above (or roughly same line) the control
    const above = c.bottom <= r.top + 8;
    const leftOf = c.right <= r.left + 8 && Math.abs(c.top - r.top) < 40;
    if (!above && !leftOf) continue;

    let dist;
    if (above) {
      const dx = Math.abs(c.left - r.left);
      const dy = r.top - c.bottom;
      dist = dy + dx * 0.5;
    } else {
      const dx = r.left - c.right;
      const dy = Math.abs(c.top - r.top);
      dist = dx + dy * 0.5;
    }
    // Penalize very short candidates: option labels like "Yes"/"No"/"Python" are
    // short; real questions are longer. This stops an option being mistaken for
    // the question when it happens to sit near the control.
    if (c.text.length < 12) dist += 60;
    // Bonus for question-like text (ends with ? or is clearly a prompt)
    if (/\?/.test(c.text)) dist -= 30;
    if (dist < bestDist) { bestDist = dist; best = c.text; }
  }
  return best;
}

// Primary label finder: try structural hints first (fast, exact), then fall
// back to spatial proximity (general, structure-independent).
function labelFor(el) {
  // 1. explicit <label for=id>
  if (el.id) {
    const lab = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
    if (lab && !lab.querySelector("input,select,textarea")) {
      const t = cleanLabel(lab.textContent);
      if (t) return t;
    }
  }
  // 2. Lever-style: ancestor containing an .application-label
  let node = el;
  for (let i = 0; i < 6; i++) {
    node = node.parentElement;
    if (!node) break;
    const labelDiv = node.querySelector(".application-label");
    if (labelDiv) {
      const textChild = labelDiv.querySelector(".text");
      const t = cleanLabel((textChild || labelDiv).textContent);
      if (t) return t;
    }
  }
  // 3. GENERAL fallback: spatial proximity (works on any site)
  const prox = labelByProximity(el);
  if (prox) return prox;
  // 4. last resort
  return cleanLabel(el.getAttribute("aria-label") || el.getAttribute("placeholder") || "");
}

function scoreField(label, patterns) {
  const l = label.toLowerCase();
  let score = 0;
  for (const p of patterns) if (l.includes(p)) score = Math.max(score, p.split(" ").length);
  return score;
}

function matchTemplate(label) {
  let best = null, bestScore = 0;
  for (const field of TEMPLATE) {
    const s = scoreField(label, field.patterns);
    if (s > bestScore) { bestScore = s; best = field.key; }
  }
  return bestScore > 0 ? best : null;
}

function fuzzyBestOption(options, desired) {
  const d = (desired || "").toLowerCase().trim();
  if (!d) return null;
  let best = null, bestScore = 0;
  for (const opt of options) {
    const text = opt.textContent.toLowerCase().trim();
    if (!text || text.includes("select")) continue;
    let score = 0;
    if (text === d) score = 100;
    else if (text.includes(d) || d.includes(text)) score = 50;
    else {
      const dWords = d.split(/\s+/);
      score = dWords.filter(w => w.length > 2 && text.includes(w)).length * 10;
    }
    if (score > bestScore) { bestScore = score; best = opt; }
  }
  return bestScore > 0 ? best : null;
}

async function selectNative(sel, desired) {
  const opt = fuzzyBestOption(Array.from(sel.options), desired);
  if (!opt) return false;
  sel.value = opt.value;
  sel.dispatchEvent(new Event("change", { bubbles: true }));
  await delay(80, 200);
  return true;
}

function radioOptionText(radio) {
  // Lever often wraps each option as <label><input type=radio> Yes</label>
  // or puts the text in a sibling span. Check all the likely spots.
  const wrap = radio.closest("label");
  if (wrap) {
    const t = cleanLabel(wrap.textContent);
    if (t) return t;
  }
  // immediate sibling(s)
  let sib = radio.nextSibling;
  while (sib) {
    if (sib.nodeType === 3) { // text node
      const t = cleanLabel(sib.textContent);
      if (t) return t;
    } else if (sib.nodeType === 1) {
      const t = cleanLabel(sib.textContent);
      if (t) return t;
    }
    sib = sib.nextSibling;
  }
  // parent's text (minus the input)
  if (radio.parentElement) {
    const t = cleanLabel(radio.parentElement.textContent);
    if (t) return t;
  }
  return cleanLabel(radio.value || "");
}

async function selectRadio(radios, desired) {
  const d = (desired || "").toLowerCase().trim();
  if (!d) return false;
  const dWords = d.split(/\s+/).filter(w => w.length > 2);
  let best = null, bestScore = 0;
  for (const radio of radios) {
    const opt = radioOptionText(radio).toLowerCase();
    if (!opt) continue;
    let score = 0;
    if (opt === d) score = 1000;
    else if (opt.includes(d) || d.includes(opt)) score = 500;
    else {
      // word-overlap score: how many of the desired words appear in the option
      const hits = dWords.filter(w => opt.includes(w)).length;
      score = hits * 10;
    }
    if (score > bestScore) { bestScore = score; best = radio; }
  }
  if (best && bestScore > 0) {
    best.click();
    // some forms need the label clicked, not the input
    const wrap = best.closest("label");
    if (wrap && !best.checked) wrap.click();
    await delay(80, 200);
    return true;
  }
  return false;
}

async function fillLocation(value) {
  if (!value) return false;
  const el = document.querySelector("#location-input, input[name=location], input.location-input");
  if (!el) return false;

  el.focus();
  el.dispatchEvent(new Event("focus", { bubbles: true }));
  await delay(150, 300);

  // type character by character with real keyboard events Lever's widget listens for
  el.value = "";
  for (const ch of value) {
    el.value += ch;
    el.dispatchEvent(new KeyboardEvent("keydown", { key: ch, bubbles: true }));
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new KeyboardEvent("keyup", { key: ch, bubbles: true }));
    await delay(40, 90);
  }
  el.dispatchEvent(new Event("change", { bubbles: true }));

  // wait for Lever's suggestion dropdown to render
  await delay(800, 1200);

  // try to click the first suggestion (Lever renders these in a dropdown list)
  const suggestion = document.querySelector(
    ".dropdown-location .dropdown-item, .location-dropdown li, " +
    "ul[role=listbox] li, .pac-item, .suggestion, [class*=location] li"
  );
  if (suggestion) {
    suggestion.click();
    await delay(150, 300);
    return true;
  }

  // no dropdown — commit the typed value with Enter + blur so the widget keeps it
  el.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", keyCode: 13, bubbles: true }));
  el.dispatchEvent(new KeyboardEvent("keyup", { key: "Enter", keyCode: 13, bubbles: true }));
  await delay(100, 200);
  el.blur();
  el.dispatchEvent(new Event("blur", { bubbles: true }));
  return true;
}

async function fillBasics(p) {
  const platform = detectPlatform();
  const r = {};
  const set = async (sel, val) => {
    const el = document.querySelector(sel);
    if (el && val) { await typeInto(el, val); return true; }
    return false;
  };
  if (platform === "greenhouse" || platform === "workday") {
    const parts = (p.name || "").split(" ");
    if (platform === "greenhouse") {
      r.first = await set("#first_name", parts[0]);
      r.last  = await set("#last_name", parts.slice(1).join(" "));
      r.email = await set("#email", p.email);
      r.phone = await set("#phone", p.phone);
    } else {
      r.first = await set("[data-automation-id=legalNameSection_firstName]", parts[0]);
      r.last  = await set("[data-automation-id=legalNameSection_lastName]", parts.slice(1).join(" "));
      r.email = await set("[data-automation-id=email]", p.email);
      r.phone = await set("[data-automation-id=phone-number]", p.phone);
    }
  } else {
    r.name  = await set("input[name=name]", p.name);
    r.email = await set("input[name=email]", p.email) || await set("input[type=email]", p.email);
    r.phone = await set("input[name=phone]", p.phone) || await set("input[name*=phone i]", p.phone);
    r.location = await fillLocation(p.location);
    r.company  = await set("input[name=org]", p.current_company);
    if (p.linkedin) r.linkedin = await set("input[name='urls[LinkedIn]']", p.linkedin);
    if (p.github)   r.github   = await set("input[name='urls[GitHub]']", p.github);
  }
  return r;
}

async function processForm(profile) {
  const filled = [];
  const proposals = [];

  const radioGroups = {};
  document.querySelectorAll("input[type=radio]").forEach(r => {
    (radioGroups[r.name] = radioGroups[r.name] || []).push(r);
  });

  for (const sel of document.querySelectorAll("select")) {
    const label = labelFor(sel);
    if (!label) continue;
    const key = matchTemplate(label);
    if (!key) continue;
    const answer = profile[key];
    if (!answer || answer === "__skip__") continue;
    const ok = await selectNative(sel, answer);
    if (ok) filled.push({ label: label.slice(0, 60), answer, type: "dropdown" });
    else proposals.push({ label: label.slice(0, 80), proposed: answer, type: "dropdown",
      options: Array.from(sel.options).map(o => o.textContent.trim()).filter(Boolean) });
  }

  for (const name in radioGroups) {
    const group = radioGroups[name];
    const label = labelFor(group[0]);
    if (!label) continue;
    if (CONSENT_PATTERNS.some(p => label.toLowerCase().includes(p))) {
      proposals.push({ label: label.slice(0, 80), proposed: "(left for you — consent)",
        type: "consent", manual: true });
      continue;
    }
    const key = matchTemplate(label);
    if (!key) continue;
    const answer = profile[key];
    if (!answer || answer === "__skip__") continue;
    const ok = await selectRadio(group, answer);
    if (ok) filled.push({ label: label.slice(0, 60), answer, type: "radio" });
    else proposals.push({ label: label.slice(0, 80), proposed: answer, type: "radio",
      options: group.map(r => labelFor(r).slice(0, 40)) });
  }

  // Label-based pass for free-text inputs, including current location / company
  // that may not use predictable name attributes.
  const LABEL_TEXT_MAP = [
    { patterns: ["current location", "your location", "where are you", "city"], key: "location" },
    { patterns: ["current company", "current employer", "present company"], key: "current_company" },
  ];
  const basicNames = ["name", "email", "phone"];
  for (const el of document.querySelectorAll("input[type=text], input:not([type]), textarea")) {
    if (basicNames.includes((el.name || "").toLowerCase())) continue;
    if (el.value) continue;
    const label = labelFor(el).toLowerCase();
    if (!label) continue;

    // first: location / company by label
    let handled = false;
    for (const m of LABEL_TEXT_MAP) {
      if (m.patterns.some(p => label.includes(p))) {
        const answer = profile[m.key];
        if (answer) { await typeInto(el, answer); filled.push({ label: label.slice(0,60), answer, type: "text" }); }
        handled = true;
        break;
      }
    }
    if (handled) continue;

    // then: template screening text fields
    const key = matchTemplate(label);
    if (!key) continue;
    const answer = profile[key];
    if (!answer || answer === "__skip__") continue;
    await typeInto(el, answer);
    filled.push({ label: label.slice(0, 60), answer, type: "text" });
  }

  return { filled, proposals };
}

async function applyProposal(prop) {
  if (prop.type === "dropdown") {
    for (const sel of document.querySelectorAll("select")) {
      if (labelFor(sel).slice(0, 80) === prop.label) return await selectNative(sel, prop.answer);
    }
  } else if (prop.type === "radio") {
    const groups = {};
    document.querySelectorAll("input[type=radio]").forEach(r => (groups[r.name] = groups[r.name] || []).push(r));
    for (const name in groups) {
      if (labelFor(groups[name][0]).slice(0, 80) === prop.label) return await selectRadio(groups[name], prop.answer);
    }
  }
  return false;
}

function send(status, message, extra = {}) {
  chrome.runtime.sendMessage({ type: "STATUS", status, message, ...extra });
}

async function run() {
  _labelCandidates = null;
  const data = await chrome.storage.sync.get("profile");
  const profile = data.profile;
  if (!profile || !profile.name) {
    send("error", "No profile saved. Open the extension, go to Profile, fill it in, and Save.");
    return;
  }
  const platform = detectPlatform();
  send("filling", `Detected ${platform}. Filling form...`);

  let basics, engine;
  try {
    basics = await fillBasics(profile);
    engine = await processForm(profile);
  } catch (e) {
    send("error", `Fill error: ${e.message}`);
    return;
  }

  const basicCount = Object.values(basics).filter(Boolean).length;
  const total = basicCount + engine.filled.length;

  if (detectCaptcha()) {
    send("captcha",
      `Filled ${total} fields. A CAPTCHA is blocking submission — solve it on the page, then click Submit.`,
      { platform, captcha: true, proposals: engine.proposals });
    return;
  }

  send("ready",
    `Filled ${total} fields automatically.` +
    (engine.proposals.length ? ` ${engine.proposals.length} question(s) need your review below.` : ` Review, then Submit.`),
    { platform, captcha: false, proposals: engine.proposals });
}

function clickSubmit() {
  for (const sel of SUBMIT_SELECTORS) {
    const btn = document.querySelector(sel);
    if (btn) { btn.click(); send("submitted", "Submit clicked. Watch the page to confirm."); return true; }
  }
  send("error", "Could not find a Submit button on this page.");
  return false;
}

chrome.runtime.onMessage.addListener((msg, _s, sendResponse) => {
  if (msg.type === "FILL_FORM") run();
  if (msg.type === "CLICK_SUBMIT") clickSubmit();
  if (msg.type === "CHECK_CAPTCHA") sendResponse({ captcha: detectCaptcha() });
  if (msg.type === "APPLY_PROPOSAL") {
    applyProposal(msg.proposal).then(ok =>
      send(ok ? "ready" : "error", ok ? `Applied: ${msg.proposal.label}` : `Could not apply: ${msg.proposal.label}`));
  }
  return true;
});

if (detectPlatform() !== "unknown") setTimeout(run, 1500);
