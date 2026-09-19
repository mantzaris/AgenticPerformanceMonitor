"use strict";
const saved = JSON.parse(document.getElementById("saved-state").textContent);
const selector = document.getElementById("reference-select");
function openEvidence(hash) {
  const target = document.getElementById(hash.replace(/^#/, ""));
  if (!target || !target.classList.contains("evidence-record")) return;
  target.open = true;
  target.scrollIntoView({block: "start"});
}
document.addEventListener("click", event => {
  const link = event.target.closest("a.evidence-link");
  if (link) openEvidence(link.getAttribute("href"));
});
if (selector) {
  const update = () => {
    const id = selector.value;
    if (!Object.prototype.hasOwnProperty.call(saved.references, id)) throw new Error("Unknown saved reference");
    const result = saved.references[id];
    document.getElementById("reference-chart").innerHTML = result.svg;
    const target = document.getElementById("reference-result");
    const explanation = target.querySelector(".change-definition");
    target.innerHTML = result.card;
    if (explanation) target.append(explanation);
    document.querySelector(".figure-surface").dataset.selectedEvidence = id;
    window.presentationState = {evidence_id:id, reference:result.reference, focal_window:result.window,
      reference_window:result.reference_window, summary:result.summary, mode:"saved-analysis-only"};
  };
  selector.addEventListener("change", update);
  update();
}
openEvidence(location.hash);
document.documentElement.dataset.presentationReady = "true";
