document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-password-toggle]");
  if (!button) return;

  const input = document.getElementById(button.dataset.passwordToggle);
  if (!input) return;

  const showing = input.type === "text";
  input.type = showing ? "password" : "text";
  button.textContent = showing ? "Mostrar" : "Ocultar";
  button.setAttribute("aria-pressed", String(!showing));

  const fieldName = input.labels?.[0]?.textContent.trim().toLowerCase() || "senha";
  button.setAttribute(
    "aria-label",
    `${showing ? "Mostrar" : "Ocultar"} ${fieldName}`,
  );
});
