document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-store-share]");
  if (!button) return;

  const url = button.dataset.shareUrl;
  const title = button.dataset.shareTitle;
  const feedback = document.querySelector("[data-share-feedback]");

  try {
    if (navigator.share) {
      await navigator.share({ title, text: `Conheça ${title}.`, url });
      if (feedback) feedback.textContent = "Loja compartilhada.";
      return;
    }
    await navigator.clipboard.writeText(url);
    if (feedback) feedback.textContent = "Link da loja copiado.";
  } catch (error) {
    if (error?.name === "AbortError") return;
    if (feedback) feedback.textContent = `Copie este link: ${url}`;
  }
});
