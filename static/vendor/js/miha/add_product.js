$(document).ready(function() {
  $('.add-to-basket-btn').on('click', function(event) {
    event.preventDefault();

    let productId = $(this).data('product-id');
    let quantity = parseInt($("#quantity_" + productId).val(), 10);
    let csrfToken = getCookie('csrftoken');

    $.ajax({
      url: '/products/baskets/add/' + productId + '/',
      type: 'POST',
      data: {
        'quantity': quantity
      },
      dataType: 'json',
      headers: {
        'X-CSRFToken': csrfToken
      },
      success: function(response) {
        console.log('Response:', response);
        console.log(response.message);
        console.log(response.available_quantity);

        if (response.available_quantity < quantity) {
          // Если заказанное количество превышает доступное, показываем уведомление о недостаточном количестве
          showNotification('warning', 'Товара недостаточно', 'Максимальное доступное количество: ' + response.available_quantity);
        } else if (response.message === 'The maximum available quantity has already been added to the basket.') {
          // Если максимальное доступное количество уже добавлено в корзину, показываем уведомление об этом
          showNotification('warning', 'Товар уже в корзине', 'Максимальное доступное количество товара уже добавлено в корзину.');
        } else {
          // Если все в порядке, показываем уведомление о том, что товар добавлен в корзину
          showNotification('success', 'Товар добавлен в корзину', 'Максимальное доступное количество: ' + response.available_quantity);
        }
      },
      error: function(xhr, status, error) {
        console.error('AJAX Error:', error);
      }
    });
  });

  function showNotification(icon, title, text) {
    Swal.fire({
      icon: icon,
      title: title,
      text: text,
      showConfirmButton: false,
      timer: 3000
    });
  }

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});