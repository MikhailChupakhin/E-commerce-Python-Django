document.addEventListener("DOMContentLoaded", function () {
    const cartButton = document.getElementById("cartButton");

    function showMessage(icon, title, timer) {
        Swal.fire({
            icon: icon,
            title: title,
            showConfirmButton: false,
            timer: timer
        });
    }

    function updateCartItems(cartItems) {
        sessionStorage.setItem("cartItems", JSON.stringify(cartItems));
        if (cartItems.length > 0) {
            cartButton.removeAttribute("disabled");
            cartButton.style.backgroundColor = "";
            cartButton.style.pointerEvents = "";
        }
    }

    function addToCart(productId, productName, quantityValue, productQuantity, productPrice) {
        const cartItems = JSON.parse(sessionStorage.getItem("cartItems")) || [];
        const foundIndex = cartItems.findIndex(item => item.productId === productId);

        if (foundIndex !== -1) {
            const newTotalQuantity = cartItems[foundIndex].quantity + quantityValue;

            if (newTotalQuantity <= productQuantity) {
                cartItems[foundIndex].quantity = newTotalQuantity;
            } else {
                cartItems[foundIndex].quantity = productQuantity;
                showMessage('warning', `Товара недостаточно: максимальное доступное количество: ${productQuantity}`, 2000);
                updateCartItems(cartItems);
                return;
            }
        } else {
            if (quantityValue <= productQuantity) {
                const newItem = {
                    productId: productId,
                    productName: productName,
                    quantity: quantityValue,
                    price: productPrice
                };
                cartItems.push(newItem);
            } else {
                showMessage('warning', `Товара недостаточно: максимальное доступное количество: ${productQuantity}`, 2000);
                return;
            }
        }

        updateCartItems(cartItems);
        showMessage('success', 'Товар добавлен в корзину', 1500);
    }

    const addToCartButtonsNoAuth = document.querySelectorAll(".add-to-cart-noauth");
    addToCartButtonsNoAuth.forEach(button => {
        button.addEventListener("click", event => {
            const button = event.target;
            const productId = button.getAttribute("data-product-id");
            const productName = button.getAttribute("data-product-name");
            const productQuantity = parseInt(button.getAttribute("data-product-quantity"));
            const productInnerElement = button.closest(".product-inner");
            const quantityInput = productInnerElement.querySelector(`#quantity_${productId}`);
            const quantityValue = quantityInput ? parseInt(quantityInput.value) : 1;
            const priceElement = productInnerElement.querySelector(`#totalPrice_${productId}`) || productInnerElement.querySelector(`#DiscountTotalPrice_${productId}`);
            const productPrice = priceElement ? parseFloat(priceElement.getAttribute("data-product-price")) : 0;

            addToCart(productId, productName, quantityValue, productQuantity, productPrice);
        });
    });
});