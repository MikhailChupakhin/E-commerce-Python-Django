$(document).ready(function () {
    const subscribeButton = $("#subscribe_button");
    const emailInput = $("#id_email");
    const csrfToken = $('[name=csrfmiddlewaretoken]').val();

    subscribeButton.on("click", function () {
        const emailValue = emailInput.val();
        if (isValidEmail(emailValue)) {
            const data = {
                csrfmiddlewaretoken: csrfToken,
                email: emailValue,
            };

            $.ajax({
                url: '/users/subscribe_news/',
                method: "POST",
                data: data,
                success: function (data) {
                    if (data.success) {
                        showNotification('success', 'Подписка создана');
                    } else {
                        showNotification('warning', 'Не удалось создать подписку');
                    }
                },
                error: function (error) {
                    showNotification('warning', 'Произошла ошибка. Возможно, вы уже подписаны?');
                }
            });
        } else {
            showNotification('error', 'Ошибка', 'Введите действительный адрес электронной почты');
        }
    });

    function isValidEmail(email) {
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        return emailPattern.test(email);
    }

    function showNotification(icon, title, text) {
        Swal.fire({
            icon: icon,
            title: title,
            text: text,
            showConfirmButton: false,
            timer: 1500
        });
    }
});