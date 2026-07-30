(() => {
  const button = document.querySelector("[data-share-site-banner]");
  if (!button) return;

  const feedback = document.querySelector("[data-share-site-feedback]");
  const setFeedback = (message) => {
    if (feedback) feedback.textContent = message;
  };

  const downloadBanner = (url) => {
    const link = document.createElement("a");
    link.href = url;
    link.download = "mercado-colatina-divulgacao.png";
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  button.addEventListener("click", async () => {
    const bannerUrl = button.dataset.bannerUrl;
    const title = button.dataset.shareTitle;
    const text = button.dataset.shareText;

    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    setFeedback("Preparando a imagem e o link...");

    try {
      const response = await fetch(bannerUrl, { cache: "force-cache" });
      if (!response.ok) throw new Error("banner_unavailable");

      const blob = await response.blob();
      const file = new File([blob], "mercado-colatina-divulgacao.png", {
        type: blob.type || "image/png",
      });
      const shareData = { files: [file], title, text };

      if (
        navigator.share &&
        navigator.canShare &&
        navigator.canShare({ files: [file] })
      ) {
        await navigator.share(shareData);
        setFeedback("Imagem e link enviados para o compartilhamento.");
        return;
      }

      downloadBanner(bannerUrl);
      let copied = false;
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        copied = true;
      }
      setFeedback(
        copied
          ? "Banner baixado e texto copiado. Anexe a imagem no WhatsApp e cole a mensagem."
          : "Banner baixado. Anexe a imagem no WhatsApp junto com o link desta página.",
      );
    } catch (error) {
      if (error && error.name === "AbortError") {
        setFeedback("Compartilhamento cancelado.");
      } else {
        setFeedback(
          "Não foi possível compartilhar automaticamente. Use o botão “Baixar o banner”.",
        );
      }
    } finally {
      button.disabled = false;
      button.removeAttribute("aria-busy");
    }
  });
})();
