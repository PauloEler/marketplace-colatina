const copyShareUrl = async (url) => {
  if (navigator.clipboard?.writeText) {
    try {
      await Promise.race([
        navigator.clipboard.writeText(url),
        new Promise((_, reject) => {
          window.setTimeout(() => reject(new Error("clipboard-timeout")), 1200);
        }),
      ]);
      return;
    } catch (_error) {
      // O navegador pode bloquear a área de transferência; usa o método compatível abaixo.
    }
  }
  const field = document.createElement("textarea");
  field.value = url;
  field.setAttribute("readonly", "");
  field.style.position = "fixed";
  field.style.opacity = "0";
  document.body.appendChild(field);
  field.select();
  if (!document.execCommand("copy")) {
    field.remove();
    throw new Error("copy-failed");
  }
  field.remove();
};

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-share-action]");
  if (!button) return;

  const panel = button.closest("[data-share-panel]");
  if (!panel) return;
  const action = button.dataset.shareAction;
  const url = panel.dataset.shareUrl || window.location.href;
  const title = panel.dataset.shareTitle || document.title;
  const text = panel.dataset.shareText || `Conheça ${title}.`;
  const feedback = panel.querySelector("[data-share-feedback]");

  try {
    if (action === "whatsapp") {
      const message = encodeURIComponent(`${text}\n${url}`);
      window.open(`https://wa.me/?text=${message}`, "_blank", "noopener,noreferrer");
      if (feedback) feedback.textContent = "WhatsApp aberto para compartilhar.";
      return;
    }
    if (action === "native" && navigator.share) {
      await navigator.share({ title, text, url });
      if (feedback) feedback.textContent = "Conteúdo compartilhado.";
      return;
    }
    await copyShareUrl(url);
    if (feedback) {
      feedback.textContent =
        action === "native"
          ? "Compartilhamento direto indisponível. Link copiado."
          : "Link copiado.";
    }
  } catch (error) {
    if (error?.name === "AbortError") return;
    if (feedback) feedback.textContent = `Copie este link: ${url}`;
  }
});
