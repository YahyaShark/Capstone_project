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
function toggleVis() {
    const inp = document.getElementById("auth_token");
    inp.type = inp.type === "password" ? "text" : "password";
}

// ── Login Twitter & ambil token otomatis ────────────────────
async function fetchToken() {
    const btn = document.getElementById("autoTokenBtn");
    const status = document.getElementById("tokenStatus");

    btn.disabled = true;
    btn.textContent = "⏳ Menunggu login…";
    status.textContent = "🌐 Browser dibuka — silakan login ke Twitter/X, token akan terdeteksi otomatis…";
    status.className = "token-status";

    try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 315_000);

        const res = await fetch("/login-twitter", { signal: controller.signal });
        clearTimeout(timer);
        const data = await res.json();

        if (data.token) {
            document.getElementById("auth_token").value = data.token;
            document.getElementById("auth_token").type = "text";
            status.textContent = "✅ Login berhasil! Token otomatis terisi.";
            status.className = "token-status ok";
        } else {
            status.textContent = data.error || "Token tidak ditemukan.";
            status.className = "token-status fail";
        }
    } catch (err) {
        status.textContent = err.name === "AbortError"
            ? "⏰ Timeout — silakan coba lagi."
            : "❌ Gagal terhubung ke server Flask.";
        status.className = "token-status fail";
    } finally {
        btn.disabled = false;
        btn.textContent = "🐦 Login Twitter & Ambil Token";
    }
}

// ── Submit ─────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();

    const query = document.getElementById("query").value.trim();
    const auth_token = document.getElementById("auth_token").value.trim();
    const max_results = parseInt(document.getElementById("max_results").value) || 20;
    const translate_to = document.getElementById("translate_to").value;

    if (!query) { showError("⚠️ Masukkan topik / hashtag yang ingin dianalisis."); return; }
    if (!auth_token) { showError("⚠️ Auth token Twitter/X wajib diisi. Lihat panduan di atas."); return; }

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
            body: JSON.stringify({ query, auth_token, max_results, translate_to }),
        });
        const data = await res.json();

        if (!res.ok || data.error) { showError(data.error || "Terjadi kesalahan."); return; }
        if (!data.tweets?.length) { showError("Tidak ada tweet ditemukan. Coba topik lain atau periksa auth_token."); return; }

        allResults = data.tweets;
        renderSummary(data.summary, data.tweets.length);
        renderTweets(allResults);

    } catch {
        showError("❌ Gagal terhubung ke server. Pastikan Flask sedang berjalan.");
    } finally {
        hide(loading);
        submitBtn.disabled = false;
    }
});

// ── Summary ────────────────────────────────────────────────
function renderSummary(s, total) {
    setText("sv-total", total);
    setText("sv-buzzer-neg", s.neg_count);          // all negative = buzzer negatif
    setText("sv-very-neg", s.very_neg_count);
    setText("sv-neg", s.neg_count - s.very_neg_count);
    setText("sv-netral", s.netral_count);
    setText("sv-positif", s.positif_count);
    setText("sp-buzzer-neg", `${s.neg_pct}% dari total`);
    setText("sp-very-neg", `${s.very_neg_pct}% dari total`);
    setText("sp-neg", `${s.neg_pct}% dari total (termasuk sangat negatif)`);

    const netralPct = total ? Math.round(s.netral_count / total * 100) : 0;
    const positifPct = total ? Math.round(s.positif_count / total * 100) : 0;

    requestAnimationFrame(() => setTimeout(() => {
        setWidth("pb-buzzer-neg", s.neg_pct);
        setWidth("pb-very-neg", s.very_neg_pct);
        setWidth("pb-neg", s.neg_pct - s.very_neg_pct);
        setWidth("pb-netral", netralPct);
        setWidth("pb-positif", positifPct);
        setText("pb-buzzer-neg-txt", `${s.neg_pct}%`);
        setText("pb-very-neg-txt", `${s.very_neg_pct}%`);
        setText("pb-neg-txt", `${Math.round((s.neg_pct - s.very_neg_pct) * 10) / 10}%`);
        setText("pb-netral-txt", `${netralPct}%`);
        setText("pb-positif-txt", `${positifPct}%`);
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
    if (type === "netral") filtered = allResults.filter(t => t.sentiment.level === 1);
    if (type === "positif") filtered = allResults.filter(t => t.sentiment.level === 0);

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
    const isBuzzerNeg = lvl >= 2;   // Negatif atau Sangat Negatif = Buzzer Negatif

    const levelClass = ["senti-positif", "senti-netral", "senti-neg", "senti-very-neg"][lvl] || "senti-netral";
    div.className = `tweet-card ${levelClass}${isBuzzerNeg ? " is-buzzer-neg" : ""}`;
    div.style.animationDelay = `${index * 0.04}s`;

    // Avatar
    const avatarHtml = t.user.profile_image
        ? `<img class="tc-avatar" src="${esc(t.user.profile_image)}" alt="avatar" onerror="this.style.display='none'">`
        : `<div class="tc-avatar-fallback">${esc((t.user.name[0] || "?").toUpperCase())}</div>`;

    // Buzzer Negatif badge (only for negative)
    const buzzerBadge = isBuzzerNeg
        ? `<span class="badge badge-buzzer-neg">🚨 Buzzer Negatif</span>`
        : "";

    // Sentiment detail badge
    const sentInfo = [
        ["🟢 Positif", "badge-positif"],
        ["⚪ Netral", "badge-netral"],
        ["🟠 Negatif", "badge-neg"],
        ["🔴 Sangat Negatif", "badge-very-neg"],
    ][lvl];
    const sentBadge = `<span class="badge ${sentInfo[1]}">${sentInfo[0]}</span>`;

    // Language badge
    const langBadge = `<span class="badge badge-lang">🌐 ${esc(t.lang.toUpperCase())}</span>`;

    // Confidence score badge (model-based only)
    const scoreBadge = t.sentiment.score != null
        ? `<span class="badge badge-score">${(t.sentiment.score * 100).toFixed(1)}% yakin</span>`
        : "";

    // Translation block
    const tgtLabel = t.translate_to === "en" ? "🇬🇧 English Translation" : "🇮🇩 Terjemahan Bahasa Indonesia";
    const translationHtml = t.translated
        ? `<div class="tc-translation">
         <span class="tl-label">🔄 ${tgtLabel}</span>
         ${esc(t.translated)}
       </div>`
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
        ${avatarHtml}
        <div>
          <div class="tc-name">${esc(t.user.name)}</div>
          <div class="tc-handle">@${esc(t.user.screen_name)}</div>
        </div>
      </div>
      <div class="badges">
        ${buzzerBadge}
        ${sentBadge}
        ${langBadge}
        ${scoreBadge}
      </div>
    </div>

    <div class="tc-text">${highlightedText}</div>

    ${kwHtml}
    ${translationHtml}

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
