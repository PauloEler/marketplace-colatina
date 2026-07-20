(() => {
  const form = document.querySelector("[data-service-request-form]");
  if (!form) return;
  const steps = [...form.querySelectorAll("[data-service-step]")];
  const label = form.querySelector("[data-step-label]");
  const progress = form.querySelector("[data-step-progress]");
  let current = 0;

  form.dataset.enhanced = "true";

  const show = (index) => {
    current = Math.max(0, Math.min(index, steps.length - 1));
    steps.forEach((step, position) => {
      step.hidden = position !== current;
    });
    label.textContent = `Passo ${current + 1} de ${steps.length}`;
    progress.style.width = `${((current + 1) / steps.length) * 100}%`;
    if (current === steps.length - 1) {
      const urgency = form.querySelector('input[name="urgencia"]:checked');
      form.querySelector("[data-review-problema]").textContent = form.elements.problema.value.trim();
      form.querySelector("[data-review-bairro]").textContent = form.elements.bairro.value.trim();
      form.querySelector("[data-review-urgencia]").textContent = urgency?.nextElementSibling.textContent || "";
      form.querySelector("[data-review-whatsapp]").textContent = form.elements.whatsapp.value.trim();
    }
    steps[current].querySelector("input, textarea, button")?.focus({ preventScroll: true });
    form.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const validCurrentStep = () => {
    const fields = [...steps[current].querySelectorAll("input, textarea, select")];
    const invalid = fields.find((field) => !field.checkValidity());
    if (invalid) invalid.reportValidity();
    return !invalid;
  };

  form.addEventListener("click", (event) => {
    if (event.target.closest("[data-next-step]")) {
      if (validCurrentStep()) show(current + 1);
    }
    if (event.target.closest("[data-previous-step]")) show(current - 1);
  });

  show(0);
})();
