function submitBuyInOneClickForm() {
    var modal = $('#buyInOneClickModal');
    var name = modal.find('#nameInput').val();
    var phone = modal.find('#phoneInput').val();
    var email = modal.find('#emailInput').val();
    var productId = modal.find('[data-product-id]').data('product-id'); // Получаем product-id из кнопки

    var csrfToken = $('[name=csrfmiddlewaretoken]').val();

    $.ajax({
        url: 'http://127.0.0.1:8000/products/buy_in_one_click/',
        type: 'POST',
        data: {
            csrfmiddlewaretoken: csrfToken,
            name: name,
            phone: phone,
            email: email,
            product_id: productId, // Передаем product-id в данных запроса
        },
        success: function (data) {
            // Вместо alert используем Swal.fire()
            Swal.fire({
                icon: 'success',
                title: 'Заявка успешно отправлена!',
                showConfirmButton: false,
                timer: 1000
            }).then(() => {
                modal.modal('hide'); // Закрываем модальное окно после таймера
                document.querySelector('#buyInOneClickModal .close').click();
            });
        },
        error: function (xhr, status, error) {
            alert('Произошла ошибка при отправке заявки.');
        }
    });
}