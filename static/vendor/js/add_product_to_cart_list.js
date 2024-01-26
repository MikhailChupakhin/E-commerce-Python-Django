document.addEventListener('DOMContentLoaded', function() {
  const addToCartListButtons = document.querySelectorAll('.add-to-cart-list');

  addToCartListButtons.forEach(button => {
    button.addEventListener('click', function(event) {
      console.log('clicked');
      event.preventDefault();

      const productId = this.getAttribute('data-product-id-list');
      const quantityInput = document.querySelector(`#quantity_${productId}-list`);
      const quantity = parseInt(quantityInput.value, 10);
      const csrfToken = getCookie('csrftoken');

      fetch(`/products/baskets/add/${productId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 'quantity': quantity })
      })
      .then(response => response.json())
      .then(response => {
        console.log('Response:', response);
        console.log(response.message);
        console.log(response.available_quantity);
        console.log(response.products_in_cart);

        const currentProductsInCart = parseInt(document.querySelector('.shopping_cart span').textContent.replace(/\D/g, ''), 10);
        const newProductsInCart = currentProductsInCart + quantity;

        document.querySelector('.shopping_cart span').textContent = `(${newProductsInCart})`;

        if (response.available_quantity < quantity) {
          showNotification('warning', 'Товара недостаточно', `Максимальное доступное количество: ${response.available_quantity}`);
        } else if (response.message === 'The maximum available quantity has already been added to the basket.') {
          showNotification('warning', 'Товар уже в корзине', 'Максимальное доступное количество товара уже добавлено в корзину.');
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