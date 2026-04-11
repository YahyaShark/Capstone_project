/* ══════════════════════════════════════════════════════════
   SentiDetect X — main.js (Sentiment Only)
   ══════════════════════════════════════════════════════════ */

"use strict";

let allResults = [];

const form = document.getElementById("analyzeForm");
const submitBtn = document.getElementById("submitBtn");
const loading = document.getElementById("loading");
const errorBanner = document.getElementById("errorBanner");
const summarySection = document.getElementById("summarySection");
const resultsSection = document.getElementById("resultsSection");
const tweetCards = document.getElementById("tweetCards");

const show = (el) => el.classList.remove("hidden");
const hide = (el) => el.classList.add("hidden");
const setText = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
const setWidth = (id, pct) => { const e = document.getElementById(id); if (e) e.style.width = pct + "%"; };

function showError(msg) {
    errorBanner.innerHTML = msg;
    show(errorBanner);
    errorBanner.scrollIntoView({ behavior: "smooth", block: "center" });
}
function clearError() { hide(errorBanner); errorBanner.innerHTML = ""; }

// ── Toggle password ────────────────────────────────────────
function toggleVis(id) {
    const inp = document.getElementById(id || "auth_token");
    if (inp) inp.type = inp.type === "password" ? "text" : "password";
}

// ── Tombol otomatis dihilangkan karena lingkungan deployment (Web/Cloud)
// ── Pengguna diwajibkan menggunakan token manual.

// ── Submit ─────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();

    const query = document.getElementById("query").value.trim();
    const auth_token = document.getElementById("auth_token").value.trim();
    const max_results = parseInt(document.getElementById("max_results").value) || 20;

    if (!query) { showError("⚠️ Please enter a topic / hashtag to analyze."); return; }
    if (!auth_token) { showError("⚠️ Twitter/X auth token is required."); return; }

    hide(summarySection);
    hide(resultsSection);
    tweetCards.innerHTML = "";
    allResults = [];

    show(loading);
    submitBtn.disabled = true;

    try {
        const res = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, auth_token, max_results }),
        });
        const data = await res.json();

        if (!res.ok || data.error) { showError(data.error || "An error occurred."); return; }
        if (!data.tweets?.length) { showError("No tweets found. Try another topic or check your auth_token & ct0."); return; }

        allResults = data.tweets;
        renderSummary(data.summary, data.tweets.length);
        renderTweets(allResults);

    } catch {
        showError("❌ Failed to connect to server. Ensure your internet connection is stable or try reloading the page.");
    } finally {
        hide(loading);
        submitBtn.disabled = false;
    }
});

// ── Summary ────────────────────────────────────────────────
function renderSummary(s, total) {
    setText("sv-total", total);
    setText("sv-buzzer-neg", s.neg_count);          // all negative = negative buzzer
    setText("sv-very-neg", s.very_neg_count);
    setText("sv-neg", s.neg_count - s.very_neg_count);
    setText("sv-neutral", s.neutral_count);
    setText("sv-positive", s.positive_count);
    setText("sp-buzzer-neg", `${s.neg_pct}%`);
    setText("sp-very-neg", `${s.very_neg_pct}%`);
    setText("sp-neg", `${s.neg_pct}% (includes very negative)`);

    const neutralPct = total ? Math.round(s.neutral_count / total * 100) : 0;
    const positivePct = total ? Math.round(s.positive_count / total * 100) : 0;

    requestAnimationFrame(() => setTimeout(() => {
        setWidth("pb-buzzer-neg", s.neg_pct);
        setWidth("pb-very-neg", s.very_neg_pct);
        setWidth("pb-neg", s.neg_pct - s.very_neg_pct);
        setWidth("pb-neutral", neutralPct);
        setWidth("pb-positive", positivePct);
        setText("pb-buzzer-neg-txt", `${s.neg_pct}%`);
        setText("pb-very-neg-txt", `${s.very_neg_pct}%`);
        setText("pb-neg-txt", `${Math.round((s.neg_pct - s.very_neg_pct) * 10) / 10}%`);
        setText("pb-neutral-txt", `${neutralPct}%`);
        setText("pb-positive-txt", `${positivePct}%`);
    }, 50));

    show(summarySection);
    show(resultsSection);
    summarySection.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Filter ─────────────────────────────────────────────────
function filterResults(type, btn) {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    let filtered = allResults;
    if (type === "buzzer-neg") filtered = allResults.filter(t => t.sentiment.level >= 2);
    if (type === "very-neg") filtered = allResults.filter(t => t.sentiment.level === 3);
    if (type === "neg") filtered = allResults.filter(t => t.sentiment.level === 2);
    if (type === "neutral") filtered = allResults.filter(t => t.sentiment.level === 1);
    if (type === "positive") filtered = allResults.filter(t => t.sentiment.level === 0);

    tweetCards.innerHTML = "";
    filtered.forEach((t, i) => tweetCards.appendChild(buildCard(t, i)));
}

// ── Render tweets ──────────────────────────────────────────
function renderTweets(tweets) {
    tweetCards.innerHTML = "";
    tweets.forEach((t, i) => tweetCards.appendChild(buildCard(t, i)));
}

// ── Build card ─────────────────────────────────────────────
function buildCard(t, index) {
    const div = document.createElement("div");
    const lvl = t.sentiment.level;
    const isBuzzerNeg = lvl >= 2;   // Negative or Very Negative = Negative Buzzer

    const levelClass = ["senti-positive", "senti-neutral", "senti-neg", "senti-very-neg"][lvl] || "senti-neutral";
    div.className = `tweet-card ${levelClass}${isBuzzerNeg ? " is-buzzer-neg" : ""}`;
    div.style.animationDelay = `${index * 0.04}s`;

    // Avatar
    const avatarHtml = t.user.profile_image
        ? `<img class="tc-avatar" src="${esc(t.user.profile_image)}" alt="avatar" onerror="this.style.display='none'">`
        : `<div class="tc-avatar-fallback">${esc((t.user.name[0] || "?").toUpperCase())}</div>`;

    // Negative Buzzer badge (only for negative)
    const buzzerBadge = isBuzzerNeg
        ? `<span class="badge badge-buzzer-neg">🚨 Negative Buzzer</span>`
        : "";

    // Sentiment detail badge
    const sentInfo = [
        ["🟢 Positive", "badge-positive"],
        ["⚪ Neutral", "badge-neutral"],
        ["🟠 Negative", "badge-neg"],
        ["🔴 Very Negative", "badge-very-neg"],
    ][lvl];
    const sentBadge = `<span class="badge ${sentInfo[1]}">${sentInfo[0]}</span>`;



    // Confidence score badge (model-based only)
    const scoreBadge = t.sentiment.score != null
        ? `<span class="badge badge-score">${(t.sentiment.score * 100).toFixed(1)}% confident</span>`
        : "";



    // Highlight negative keywords in original text
    let highlightedText = esc(t.text);
    (t.sentiment.neg_keywords || []).forEach(kw => {
        const re = new RegExp(kw.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
        highlightedText = highlightedText.replace(re, `<span class="kw-neg">$&</span>`);
    });
    (t.sentiment.pos_keywords || []).forEach(kw => {
        const re = new RegExp(kw.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
        highlightedText = highlightedText.replace(re, `<span class="kw-pos">$&</span>`);
    });

    // Keyword badges (only for neg)
    const kwHtml = t.sentiment.neg_keywords?.length
        ? `<div class="tc-keywords">
        ${t.sentiment.neg_keywords.map(k => `<span class="kw-badge">${esc(k)}</span>`).join("")}
       </div>`
        : "";

    div.innerHTML = `
    <div class="tc-top">
      <div class="tc-user">
        <a href="https://x.com/${esc(t.user.screen_name)}" target="_blank" title="Buka Profil Asli">
          ${avatarHtml}
        </a>
        <div>
          <div class="tc-name">
            <a href="https://x.com/${esc(t.user.screen_name)}" target="_blank" style="text-decoration:none; color:inherit;">
              ${esc(t.user.name)}
            </a>
          </div>
          <div class="tc-handle">@${esc(t.user.screen_name)} • ${fmt(t.user.followers)} followers</div>
        </div>
      </div>
      <div class="badges">
        ${buzzerBadge}
        ${sentBadge}
        ${scoreBadge}
      </div>
    </div>

    <div class="tc-text">${highlightedText}</div>

    ${kwHtml}

    <div class="tc-metrics">
      <div class="metric"><span>🔁</span><span class="metric-val">${fmt(t.metrics.retweet_count)}</span>&nbsp;RT</div>
      <div class="metric"><span>❤️</span><span class="metric-val">${fmt(t.metrics.like_count)}</span>&nbsp;Like</div>
      <div class="metric"><span>💬</span><span class="metric-val">${fmt(t.metrics.reply_count)}</span>&nbsp;Reply</div>
      <div class="metric"><span>🔗</span><span class="metric-val">${fmt(t.metrics.quote_count)}</span>&nbsp;Quote</div>
    </div>
  `;

    return div;
}

// ── Utils ──────────────────────────────────────────────────
function esc(str) {
    return String(str)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function fmt(n) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
    if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
    return String(n);
}
