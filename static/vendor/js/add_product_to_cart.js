document.addEventListener('DOMContentLoaded', function() {
  const addToCartButtons = document.querySelectorAll('.add-to-cart');

  addToCartButtons.forEach(button => {
    button.addEventListener('click', function(event) {
      console.log('clicked');
      event.preventDefault();

      const productId = this.getAttribute('data-product-id');
      const quantity = parseInt(document.querySelector(`#quantity_${productId}`).value, 10);
      const isAuthenticated = parseInt(this.getAttribute('data-authenticated'));
      const csrfToken = getCookie('csrftoken');

      let url;
      if (isAuthenticated === 1) {
        url = `/products/baskets/add/${productId}/`;
      } else {
        url = `/products/baskets/add_anonymous/${productId}/`;
      }

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 'quantity': quantity })
      })
      .then(response => {
        if (response.status === 400) {
          return response.json().then(data => {
            showNotification('error', 'Ошибка', data.error);
            throw new Error(data.error);
          });
        }
        return response.json();
      })
      .then(response => {
        console.log('Response:', response);
        console.log(response.message);
        console.log(response.available_quantity);
        console.log(response.products_in_cart);

        // Обновление счетчика корзины
        const cartCountElement = document.querySelector('.shopping_cart span');
        if (cartCountElement) {
          const currentProductsInCart = parseInt(cartCountElement.textContent.replace(/\D/g, ''), 10);
          const newProductsInCart = currentProductsInCart + quantity;

          cartCountElement.textContent = `(${newProductsInCart})`;
        }

        if (response.available_quantity < quantity) {
          showNotification('warning', 'Товара недостаточно', `Максимальное доступное количество добавлено в корзину: ${response.available_quantity}`);
        } else if (response.message === 'The maximum available quantity has already been added to the basket.') {
          showNotification('warning', 'Товар уже в корзине', 'Максимальное доступное количество товара добавлено в корзину.');
        } else if (response.message === 'Invalid quantity') {
          showNotification('error', 'Сожалеем', 'Этот товар закончился');
        } else {
          showNotification('success', 'Товар добавлен в корзину', `Максимальное доступное количество: ${response.available_quantity}`);
        }
      })
      .catch(error => {
        console.error('Fetch Error:', error);
      });
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