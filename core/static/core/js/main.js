document.addEventListener("DOMContentLoaded", function () {
  const modalTriggers = document.querySelectorAll("[data-modal-target]");
  const closeButtons = document.querySelectorAll(".modal-close");

  modalTriggers.forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.querySelector(button.dataset.modalTarget);
      if (target) target.classList.add("modal-open");
    });
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const modal = button.closest(".modal");
      if (modal) modal.classList.remove("modal-open");
    });
  });
});
