$(document).ready(function () {
    // Функция для проверки длины значения поля и отображения сообщений об ошибках
    function validateField(field, maxLength, errorMessage, regexPattern) {
        if (field.val().length > maxLength || (regexPattern && !regexPattern.test(field.val()))) {
             field.addClass('is-invalid');
             field.next('.invalid-feedback').text(errorMessage);

             // Добавляем всплывающее окно (popover) с сообщением об ошибке
             field.popover({
                 content: errorMessage,
                 trigger: 'focus', // Всплывающее окно будет показано при фокусировке на поле
                 placement: 'top', // Размещаем всплывающее окно над полем
             });
             field.popover('show'); // Показываем всплывающее окно

             return false;
        } else {
            field.removeClass('is-invalid');
            field.next('.invalid-feedback').text('');

            // Удаляем всплывающее окно, если оно было создано
            field.popover('dispose');

            return true;
        }
    }

    // Проверка поля Имя
    $('#id_first_name').on('input', function () {
        validateField($(this), 50, 'Имя не может быть длиннее 50 символов.');
    });

    // Проверка поля Фамилия
    $('#id_last_name').on('input', function () {
        validateField($(this), 50, 'Фамилия не может быть длиннее 50 символов.');
    });

    // Проверка поля Email
    $('#id_email').on('input', function () {
        var emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        validateField($(this), 120, 'Email должен соответствовать формату example@example.com и не может быть длиннее 120 символов.', emailPattern);
    });

    // Проверка поля Адрес
    $('#id_address').on('input', function () {
        validateField($(this), 250, 'Адрес не может быть длиннее 250 символов.');
    });

    // Проверка поля Телефон
    $('#id_phone').on('input', function () {
        // Примеры разрешенных форматов телефона: 81234567890 или +71234567890
        var phonePattern = /^\+7\d{10}$/;
        validateField($(this), 13, 'Номер телефона должен соответствовать форматам 81234567890 или +71234567890.', phonePattern);
    });

    // Обработка отправки формы
    $('form').on('submit', function (e) {
        // Проверяем поля перед отправкой на сервер
        var isValid = true;

        isValid = isValid && validateField($('#id_first_name'), 50, 'Имя не может быть длиннее 50 символов.');
        isValid = isValid && validateField($('#id_last_name'), 50, 'Фамилия не может быть длиннее 50 символов.');
        isValid = isValid && validateField($('#id_email'), 256, 'Email не может быть длиннее 256 символов.');
        isValid = isValid && validateField($('#id_address'), 250, 'Адрес не может быть длиннее 250 символов.');
        isValid = isValid && validateField($('#id_phone'), 13, 'Номер телефона не может быть длиннее 13 символов.');

        if (!isValid) {
            e.preventDefault(); // Отменяем отправку формы на сервер, если есть ошибки
        }
    });

    // Убедитесь, что всплывающие окна исчезают при фокусировке на поле
    $('input').on('focus', function () {
        $(this).popover('dispose');
    });
});