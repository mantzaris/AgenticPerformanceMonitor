"use strict";
// Every state is an already selected, saved result. No network or analysis calls.
const saved = JSON.parse(document.getElementById("saved-state").textContent);
const selector = document.getElementById("reference-select");
function openEvidence(hash) {
  const target = document.getElementById(hash.replace(/^#/, ""));
  if (!target || !target.classList.contains("evidence-record")) return;
  for (let parent = target.parentElement; parent; parent = parent.parentElement)
    if (parent.tagName === "DETAILS") parent.open = true;
  target.open = true;
  target.scrollIntoView({block: "start"});
}
document.addEventListener("click", event => {
  const link = event.target.closest("a.evidence-link");
  if (link) openEvidence(link.getAttribute("href"));
});
window.addEventListener("hashchange", () => openEvidence(location.hash));
if (selector) {
  const chart = document.getElementById("reference-chart");
  const result = document.getElementById("reference-result");
  const warning = document.getElementById("reference-warning");
  const permalink = document.getElementById("saved-permalink");
  const explanation = result.querySelector(".change-definition");
  const update = (id, changeUrl) => {
    if (!Object.prototype.hasOwnProperty.call(saved.references, id)) {
      selector.selectedIndex = -1;
      chart.hidden = result.hidden = permalink.hidden = true;
      warning.hidden = false;
      warning.textContent = "This reference is not among the saved selected results. Choose an available saved reference.";
      window.presentationState = {error: "unknown_saved_reference", requested: id, mode: "saved-analysis-only"};
      return;
    }
    selector.value = id;
    const value = saved.references[id];
    chart.hidden = result.hidden = permalink.hidden = false;
    warning.hidden = true;
    chart.innerHTML = value.svg;
    result.innerHTML = value.card;
    if (explanation) result.append(explanation);
    document.querySelector(".figure-surface").dataset.selectedEvidence = id;
    window.presentationState = {evidence_id: id, reference: value.reference,
      focal_window: value.window, reference_window: value.reference_window,
      summary: value.summary, mode: "saved-analysis-only"};
    const url = new URL(location.href);
    url.searchParams.set("reference", id);
    url.hash = "";
    permalink.href = url.href;
    if (changeUrl) history.replaceState(null, "", url.href);
  };
  selector.addEventListener("change", () => update(selector.value, true));
  const requested = new URL(location.href).searchParams.get("reference");
  update(requested === null ? selector.value : requested, false);
}
openEvidence(location.hash);
document.documentElement.dataset.presentationReady = "true";
