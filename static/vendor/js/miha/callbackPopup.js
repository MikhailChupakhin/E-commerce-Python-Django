document.addEventListener("DOMContentLoaded", function() {
  // Функция для отображения модального окна
  function showModal() {
    document.getElementById("callbackModal").style.display = "block";
  }

  // Добавляем обработчик клика на кнопку "Перезвоните мне"
  document.querySelector(".btn-call-me").addEventListener("click", function() {
    showModal();
  });

  // Добавляем обработчик отправки формы
  document.getElementById("callback-form").addEventListener("submit", function(event) {
    event.preventDefault(); // Отменяем стандартное действие отправки формы

    // Получаем значения полей формы
    const name = document.getElementById("name").value;
    const phone = document.getElementById("phone").value;

    // Получаем URL API-эндпоинта из атрибута data-api-endpoint-url
    const apiEndpointUrl = document.getElementById("api-endpoint-url").value;

    // Создаем объект данных для отправки
    const formData = {
      name: name,
      phone: phone,
      csrfmiddlewaretoken: document.querySelector("input[name='csrfmiddlewaretoken']").value
    };

    // Отправляем AJAX-запрос на сервер для сохранения данных в БД
    fetch(apiEndpointUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": formData.csrfmiddlewaretoken
      },
      body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
      // В данном примере, предполагается что сервер вернет JSON с сообщением об успешном сохранении
      if (data.success) {
        console.log(data.success)
        // Закрываем модальное окно после успешного сохранения
        document.getElementById("callbackModal").style.display = "none";
        // Очищаем поля формы
        document.getElementById("name").value = "";
        document.getElementById("phone").value = "";

        // Показываем уведомление пользователю
        showNotification("Заявка принята. С вами свяжутся в ближайшее время.");

        // Здесь можно добавить дополнительную обработку после успешного сохранения
      } else {
        // В случае ошибки, здесь можно добавить обработку ошибки
      }
    })
    .catch(error => {
      console.error("Error:", error);
    });
  });

  // Добавляем обработчик клика на кнопку "Отмена" внутри модального окна
  document.querySelector(".modal .btn.btn-secondary").addEventListener("click", function() {
    document.getElementById("callbackModal").style.display = "none";
  });

  // Добавляем обработчик клика на крестик внутри модального окна
  document.querySelector(".modal #close-cross").addEventListener("click", function() {
    document.getElementById("callbackModal").style.display = "none";
  });

  // Функция для отображения всплывающего уведомления
  function showNotification(message) {
    // Создаем элемент уведомления
    const notificationElement = document.getElementById("notification");

    notificationElement.textContent = message;

    notificationElement.style.display = "block";

    // Удаляем уведомление через 5 секунд
    setTimeout(function() {
      notificationElement.style.display = "none";
    }, 3000);
  }
});