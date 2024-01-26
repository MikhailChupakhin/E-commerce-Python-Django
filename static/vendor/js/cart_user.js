document.addEventListener('DOMContentLoaded', function() {
  const userId = document.getElementById('user-id').value;

  function showNotification(icon, title, text) {
    Swal.fire({
      icon: icon,
      title: title,
      text: text,
      showConfirmButton: false,
      timer: 3000
    });
  }

  function bindDeleteButtonHandlers() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
      button.addEventListener('click', function() {
        const productId = this.getAttribute('data-product-id');
        const selectedDeliveryPrice = parseFloat(document.querySelector('.selected_delivery_price').textContent);
        deleteCartItem(productId, selectedDeliveryPrice);
      });
    });
  }

  function updateTotalWithDelivery(selectedDeliveryPrice) {
    const cartItemsTotal = parseFloat(document.querySelector('.cart_items_total_price').textContent.replace(',', '.'));
    const newCartSumValue = cartItemsTotal + selectedDeliveryPrice;
    const cartSumValue = document.querySelector('.order_total_price.ml-auto');
    cartSumValue.textContent = newCartSumValue.toFixed(2);
  }

  bindDeleteButtonHandlers();

  const quantityChangeButtons = document.querySelectorAll('.quantity-change-btn');
  quantityChangeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const productId = this.getAttribute('data-product-id');
      const changeType = this.getAttribute('data-type');
      const selectedDeliveryPrice = parseFloat(document.querySelector('.selected_delivery_price').textContent);
      changeCartItemQuantity(productId, changeType, selectedDeliveryPrice);
    });
  });

  function deleteCartItem(productId, selectedDeliveryPrice) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const url = `/users/cart/${userId}/remove/`;

    const data = {
      csrfmiddlewaretoken: csrfToken,
      product_id: productId,
    };

    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(updatedCart => {
      const cartItemToRemove = document.querySelector(`[data-product-id="${productId}"]`).closest('.cart_item');
      cartItemToRemove.remove();

      const cartTotalValue = document.querySelector('.cart_total_value.cart_items_total_price.ml-auto');
      const newCartTotalValue = updatedCart.order_total_price;
      cartTotalValue.textContent = newCartTotalValue;

      const cartSumValue = document.querySelector('.cart_total_value.ml-auto:last-child');
      const newCartSumValue = parseFloat(newCartTotalValue);
      cartSumValue.textContent = newCartSumValue.toFixed(2);
      updateTotalWithDelivery(selectedDeliveryPrice);
      bindDeleteButtonHandlers();
    })
    .catch(error => {
      console.error('Failed to delete item from cart.', error);
    });
  }

  function changeCartItemQuantity(productId, changeType, selectedDeliveryPrice) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const url = `/users/cart/${userId}/update/`;

    const data = {
      csrfmiddlewaretoken: csrfToken,
      product_id: productId,
      quantity_change_type: changeType
    };

    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(response => {
      if (response.error && response.error === "Exceeded available quantity for this product") {
        showNotification('warning', 'Товара недостаточно', 'Максимальное доступное количество добавлено в корзину.');
      } else {
        const productItem = response.updated_cart.cart_items.find(item => item.product_id.toString() === productId);
        if (productItem && productItem.quantity !== undefined) {
          const newQuantity = productItem.quantity;
          const quantityInput = document.querySelector(`input.quantity_input[data-product-id='${productId}']`);
          quantityInput.value = newQuantity;

          const cartItemTotal = document.querySelector(`.cart_item_total[data-product-id='${productId}']`);
          const newTotalValue = (newQuantity * productItem.price).toFixed(2);
          cartItemTotal.textContent = newTotalValue;

          const cartTotalValue = document.querySelector('.cart_total_value.cart_items_total_price.ml-auto');
          const newCartTotalValue = response.order_total_price;
          cartTotalValue.textContent = newCartTotalValue;
          // Обновление суммы с учетом доставки
          const cartSumValue = document.querySelector('.cart_total_value.ml-auto:last-child');
          const newCartSumValue = parseFloat(newCartTotalValue);
          cartSumValue.textContent = newCartSumValue.toFixed(2);
          updateTotalWithDelivery(selectedDeliveryPrice);
        }
      }
    })
    .catch(error => {
      console.error('Failed to update item quantity in cart.', error);
    });
  }

  function saveDeliveryToSession(deliveryMethodId, deliveryPrice) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const url = `/users/save_delivery/`;

    const data = {
      deliveryMethodId: deliveryMethodId,
    };

    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(() => {
      window.location.href = '/orders/checkout/';
    })
    .catch(error => {
      console.error('Ошибка при сохранении данных в сессии:', error);
    });
  }

  const checkoutButton = document.getElementById('checkout-button');
  checkoutButton.addEventListener('click', function(event) {
    event.preventDefault();

    const selectedRadio = document.querySelector('input[name="radio"]:checked');

    if (selectedRadio) {
      const deliveryMethodId = selectedRadio.getAttribute('data-delivery-method-id');
      const deliveryPrice = selectedRadio.getAttribute('data-delivery-price');

      saveDeliveryToSession(deliveryMethodId, deliveryPrice);
    }
  });

  const deliveryOptions = document.querySelectorAll('.delivery_option input[name="radio"]');
  deliveryOptions.forEach(option => {
    option.addEventListener('change', function() {
      const selectedDeliveryPrice = parseFloat(this.parentElement.querySelector('.delivery_price').textContent);
      const selectedDeliveryPriceElement = document.getElementById('selected_delivery_price');
      selectedDeliveryPriceElement.textContent = selectedDeliveryPrice.toFixed(2);
      updateTotalWithDelivery(selectedDeliveryPrice);
    });
  });
});