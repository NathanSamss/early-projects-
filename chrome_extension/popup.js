// popup.js — drives the popup, profile/screening storage, and proposal review

const FIELDS = [
  "name", "email", "phone", "location", "current_company", "linkedin", "github", "cover_letter",
  "work_authorization", "visa_type", "availability", "salary_expectation", "preferred_language",
  "relocate", "years_experience", "how_heard", "dei_gender", "dei_ethnicity", "dei_age",
];

document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add("active");
  });
});

const statusEl = document.getElementById("status");
const submitBtn = document.getElementById("btn-submit");
const proposalsEl = document.getElementById("proposals");

function setStatus(status, message) {
  statusEl.className = `status ${status}`;
  statusEl.textContent = message;
  submitBtn.disabled = !(status === "ready" || status === "captcha");
}

async function activeTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

function renderProposals(proposals) {
  proposalsEl.innerHTML = "";
  if (!proposals || !proposals.length) return;
  const head = document.createElement("div");
  head.className = "section";
  head.textContent = "Review needed";
  proposalsEl.appendChild(head);

  proposals.forEach((prop, i) => {
    const box = document.createElement("div");
    box.className = "proposal";
    const q = document.createElement("div");
    q.className = "q";
    q.textContent = prop.label;
    box.appendChild(q);

    if (prop.manual) {
      const note = document.createElement("div");
      note.className = "manual-note";
      note.textContent = "Left for you to handle on the page (consent / legal).";
      box.appendChild(note);
      proposalsEl.appendChild(box);
      return;
    }

    const a = document.createElement("div");
    a.className = "a";
    a.textContent = "Proposed: " + prop.proposed;
    box.appendChild(a);

    const input = document.createElement("input");
    input.value = prop.proposed;
    input.id = `prop-${i}`;
    box.appendChild(input);

    if (prop.options && prop.options.length) {
      const opts = document.createElement("div");
      opts.className = "hint";
      opts.textContent = "Options: " + prop.options.filter(Boolean).join(", ");
      box.appendChild(opts);
    }

    const row = document.createElement("div");
    row.className = "prow";
    const applyBtn = document.createElement("button");
    applyBtn.className = "apply";
    applyBtn.textContent = "Apply";
    applyBtn.onclick = async () => {
      const tab = await activeTab();
      const answer = document.getElementById(`prop-${i}`).value;
      await chrome.tabs.sendMessage(tab.id, {
        type: "APPLY_PROPOSAL",
        proposal: { ...prop, answer },
      });
      applyBtn.textContent = "Applied";
      applyBtn.disabled = true;
    };
    const skipBtn = document.createElement("button");
    skipBtn.className = "skip";
    skipBtn.textContent = "Skip";
    skipBtn.onclick = () => box.remove();
    row.appendChild(applyBtn);
    row.appendChild(skipBtn);
    box.appendChild(row);

    proposalsEl.appendChild(box);
  });
}

document.getElementById("btn-fill").addEventListener("click", async () => {
  setStatus("filling", "Filling form...");
  proposalsEl.innerHTML = "";
  const tab = await activeTab();
  try {
    await chrome.tabs.sendMessage(tab.id, { type: "FILL_FORM" });
  } catch {
    setStatus("error", "Cannot reach the page. Refresh it and try again.");
  }
});

let submitWarned = false;
submitBtn.addEventListener("click", async () => {
  const tab = await activeTab();
  try {
    const res = await chrome.tabs.sendMessage(tab.id, { type: "CHECK_CAPTCHA" });
    if (res && res.captcha && !submitWarned) {
      submitWarned = true;
      setStatus("captcha", "A visible CAPTCHA was detected. If you have already solved it (or there is no puzzle), click Submit once more to proceed.");
      return;
    }
    submitWarned = false;
    await chrome.tabs.sendMessage(tab.id, { type: "CLICK_SUBMIT" });
  } catch {
    setStatus("error", "Cannot reach the page. Refresh and try again.");
  }
});

chrome.runtime.onMessage.addListener(msg => {
  if (msg.type === "STATUS") {
    setStatus(msg.status, msg.message);
    if (msg.proposals) renderProposals(msg.proposals);
  }
});

async function loadProfile() {
  const data = await chrome.storage.sync.get("profile");
  const p = data.profile || {};
  FIELDS.forEach(f => {
    const el = document.getElementById(`p-${f}`);
    if (el && p[f] !== undefined) el.value = p[f];
  });
  // sensible DEI defaults
  ["dei_gender", "dei_ethnicity", "dei_age"].forEach(f => {
    const el = document.getElementById(`p-${f}`);
    if (el && !el.value) el.value = "Prefer not to say";
  });
}

async function saveProfile(msgId) {
  const data = await chrome.storage.sync.get("profile");
  const profile = data.profile || {};
  FIELDS.forEach(f => {
    const el = document.getElementById(`p-${f}`);
    if (el) profile[f] = el.value.trim();
  });
  await chrome.storage.sync.set({ profile });
  const msg = document.getElementById(msgId);
  msg.textContent = "Saved.";
  setTimeout(() => { msg.textContent = ""; }, 2000);
}

document.getElementById("btn-save").addEventListener("click", () => saveProfile("save-msg"));
document.getElementById("btn-save2").addEventListener("click", () => saveProfile("save-msg2"));

(async () => {
  const tab = await activeTab();
  const status = await chrome.runtime.sendMessage({ type: "GET_STATUS", tabId: tab.id });
  if (status) setStatus(status.status, status.message);
  loadProfile();
})();
