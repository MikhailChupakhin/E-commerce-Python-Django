var productId; // Объявляем переменную в глобальной области видимости

$(document).ready(function() {
    $('#buyInOneClickModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        productId = button.data('product-id');
        var modal = $(this);
    });
});

function submitBuyInOneClickForm() {
    var modal = $('#buyInOneClickModal');
    var name = modal.find('#nameInput').val();
    var phone = modal.find('#phoneInput').val();
    var email = modal.find('#emailInput').val();

    var csrfToken = $('[name=csrfmiddlewaretoken]').val();

    $.ajax({
        url: 'buy_in_one_click/',
        type: 'POST',
        data: {
            csrfmiddlewaretoken: csrfToken,
            name: name,
            phone: phone,
            email: email,
            product_id: productId, // Теперь productId доступна здесь
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