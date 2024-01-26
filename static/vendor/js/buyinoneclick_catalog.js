var productId = null;

function passProductId(element) {
    productId = element.getAttribute('data-product-id');
}

function submitBuyInOneClickForm() {
    var modal = document.getElementById('buyInOneClickModal');
    var nameInput = modal.querySelector('#nameInput');
    var phoneInput = modal.querySelector('#phoneInput');
    var emailInput = modal.querySelector('#emailInput');
    var url = 'buy_in_one_click/';
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

     var requestData = {
        name: nameInput.value,
        phone: phoneInput.value,
        email: emailInput.value,
        product_id: productId
    };

    fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(requestData)
    })
    .then(function (response) {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Произошла ошибка при отправке заявки.');
        }
    })
    .then(function (data) {
        if (data.status === 'success') {
            Swal.fire({
                icon: 'success',
                title: 'Заявка успешно отправлена!',
                showConfirmButton: false,
                timer: 1000
            }).then(function () {
                modal.style.display = 'none';
                document.querySelector('#buyInOneClickModal .close').click();
            });
        } else {
            throw new Error('Произошла ошибка при отправке заявки.');
        }
    })
    .catch(function (error) {
        alert(error.message);
    });
}