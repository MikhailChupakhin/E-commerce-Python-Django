// feedbackPopup.js
document.addEventListener("DOMContentLoaded", function() {
  // Функция для отображения модального окна
  function showModal() {
    document.getElementById("feedbackModal").style.display = "block";
  }

  // Задаем таймер для показа
  setTimeout(showModal, 180000);

  // Обработчик клика на кнопку "Заполнить форму обратной связи"
  document.getElementById("feedbackButton").onclick = function() {
    // Перенаправляем пользователя на страницу заполнения формы обратной связи
    window.location.href = "/users/feedback/"; // Вставляем URL шаблон для feedback_view
  };

  // Обработчик клика на кнопку закрытия модального окна
  document.getElementById("closeModal").onclick = function() {
    document.getElementById("feedbackModal").style.display = "none";
  };
});