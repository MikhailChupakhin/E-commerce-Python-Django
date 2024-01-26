$(document).ready(function() {
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
        $(".delete-btn").on("click", function() {
            console.log('clicked');
            const productId = $(this).data("product-id");
            deleteCartItem(productId);
        });
    }

    bindDeleteButtonHandlers();

    $(".quantity-change-btn").on("click", function() {
        const productId = $(this).data("product-id");
        const changeType = $(this).data("type");
        console.log('ATTENTION!', productId, changeType);
        changeCartItemQuantity(productId, changeType);
    });

    function deleteCartItem(productId) {
        const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        let url = '/users/cart_guest/remove/' + productId + '/';
        $.ajax({
            url: url,
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            },
            success: function(updated_cart) {
                const cartItemToRemove = $(`[data-product-id="${productId}"]`).closest('.cart_item');
                cartItemToRemove.remove();

                // Обновление общей стоимости корзины
                const cartTotalValue = $(".cart_total_value.cart_items_total_price.ml-auto");
                const newCartTotalValue = updated_cart.order_total_price;
                cartTotalValue.text(newCartTotalValue);

                // Обновление суммы с учетом доставки
                const deliveryCost = 500; // Стоимость доставки
                const cartSumValue = $(".cart_total_value.ml-auto").last(); // Элемент суммы
                const newCartSumValue = parseFloat(newCartTotalValue) + deliveryCost;
                cartSumValue.text(newCartSumValue.toFixed(2));
                bindDeleteButtonHandlers();
            },
            error: function() {
                console.error("Failed to delete item from cart.");
            }
        });
    }

    function changeCartItemQuantity(productId, changeType) {
        const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        let url = '/users/cart_guest/update/';
        const data = {
            csrfmiddlewaretoken: csrfToken,
            product_id: productId,
            quantity_change_type: changeType
        };
        $.ajax({
            url: url,
            method: "POST",
            data: data,
            success: function(response) {
                if (response.error && response.error === "Exceeded available quantity for this product") {
                    showNotification('warning', 'Товара недостаточно', 'Максимальное доступное количество добавлено в корзину.');
                } else {
                    const productItem = response.updated_cart.cart_items.find(item => item.product_id === productId);
                    if (productItem && productItem.quantity !== undefined) {
                        const newQuantity = productItem.quantity;
                        const quantityInput = $(`input.quantity_input[data-product-id='${productId}']`);
                        quantityInput.val(newQuantity);
                        // Обновление поля cart_item_total
                        const cartItemTotal = $(`.cart_item_total[data-product-id='${productId}']`);
                        const newTotalValue = (newQuantity * productItem.price).toFixed(2);
                        cartItemTotal.text(newTotalValue);
                        // Обновление общей стоимости корзины
                        const cartTotalValue = $(".cart_total_value.cart_items_total_price.ml-auto");
                        const newCartTotalValue = response.order_total_price;
                        cartTotalValue.text(newCartTotalValue);
                        // Обновление суммы с учетом доставки
                        const deliveryCost = 500; // Стоимость доставки
                        const cartSumValue = $(".cart_total_value.ml-auto").last(); // Элемент суммы
                        const newCartSumValue = parseFloat(newCartTotalValue) + deliveryCost;
                        cartSumValue.text(newCartSumValue.toFixed(2));
                    }
                }
            },
            error: function() {
                console.error("Failed to update item quantity in cart.");
            }
        });
    }

    function updateTotalWithDelivery(selectedDeliveryPrice) {
        const cartItemsTotal = parseFloat($(".cart_items_total_price").text().replace(',', '.'));
        const newCartSumValue = cartItemsTotal + selectedDeliveryPrice;
        const cartSumValue = $(".cart_total_value.ml-auto").last();
        cartSumValue.text(newCartSumValue.toFixed(2));
    }

    function saveDeliveryToSession(deliveryMethodId, deliveryPrice) {
        const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        const url = `/users/save_delivery/`;
        $.ajax({
            url: url,
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: JSON.stringify({
                deliveryMethodId: deliveryMethodId,
            }),
            success: function(response) {
                window.location.href = '/orders/checkout/';
            },
            error: function(error) {
                console.error('Ошибка при сохранении данных в сессии:', error);
            }
        });
    }

    const checkoutButton = $('#checkout-button');
    checkoutButton.on('click', function(event) {
    console.log('clicked')
        event.preventDefault();

        const selectedRadio = $('input[name="radio"]:checked');

        if (selectedRadio.length > 0) {
            const deliveryMethodId = selectedRadio.attr('data-delivery-method-id');
            const deliveryPrice = selectedRadio.attr('data-delivery-price');

            saveDeliveryToSession(deliveryMethodId, deliveryPrice);
        }
    });

    // Получаем элемент, в который будем выводить стоимость доставки
    const selectedDeliveryPriceElement = document.getElementById('selected_delivery_price');

    // Обработчик изменения выбранного способа доставки
    const deliveryOptions = document.querySelectorAll('.delivery_option input[name="radio"]');
    deliveryOptions.forEach(option => {
        option.addEventListener('change', function() {
            const selectedDeliveryPrice = parseFloat(this.parentElement.querySelector('.delivery_price').textContent);
            selectedDeliveryPriceElement.textContent = selectedDeliveryPrice.toFixed(2);
            updateTotalWithDelivery(selectedDeliveryPrice);
        });
    });
});