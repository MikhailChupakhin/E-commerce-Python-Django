var url = '/users/callback/';

document.addEventListener('DOMContentLoaded', function () {
    var callbackModal = document.querySelector('#CallbackModal');

    callbackModal.addEventListener('show.bs.modal', function (event) {
        url = '/users/callback/'; // Обновляем значение переменной внутри обработчика события
    });
});

function submitCallbackForm() {
    var callbackModal = document.querySelector('#CallbackModal');
    var nameInput = callbackModal.querySelector('#nameInput');
    var phoneInput = callbackModal.querySelector('#phoneInput');
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Проверяем, что обязательные поля заполнены
    if (!nameInput.value || !phoneInput.value) {
        alert('Заполните обязательные поля.');
        return;
    }

    // Создание объекта с данными для отправки в формате JSON
    var requestData = {
        csrfmiddlewaretoken: csrfToken,
        name: nameInput.value,
        phone: phoneInput.value
    };

    fetch(url, {
        method: 'POST',
        body: JSON.stringify(requestData), // Преобразование объекта в JSON
        headers: {
            'Content-Type': 'application/json' // Установка заголовка Content-Type
        }
    })
    .then(function (response) {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Произошла ошибка при отправке заявки.');
        }
    })
    .then(function (data) {
        Swal.fire({
            icon: 'success',
            title: 'Заявка успешно отправлена!',
            showConfirmButton: false,
            timer: 1000
        }).then(function () {
            callbackModal.classList.remove('show');
            callbackModal.style.display = 'none';
            document.querySelector('#CallbackModal .close').click();
        });
    })
    .catch(function (error) {
        alert(error.message);
    });
}