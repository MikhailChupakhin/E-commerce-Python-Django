document.addEventListener("DOMContentLoaded", function () {
    const addToCartButtonsNoAuth = document.querySelectorAll(".add-to-cart-noauth");
    const cartButton = document.getElementById("cartButton");

    addToCartButtonsNoAuth.forEach(function (button) {
        button.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default link behavior

            const button = event.target;
            const productId = button.getAttribute("data-product-id");

            // Find the closest parent that contains the product information
            const productCard = button.closest(".product-card");

            // Get the product price from the price element within the product card
            const priceElement = productCard.querySelector(".total-price");
            const productPrice = priceElement ? parseFloat(priceElement.getAttribute("data-product-price")) : 0;

            // Get the quantity value from the input within the product card
            const quantityInput = productCard.querySelector(".quantity-input");
            const quantityValue = quantityInput ? parseInt(quantityInput.value) : 1;

            // Update sessionStorage after adding the product
            const cartItems = JSON.parse(sessionStorage.getItem("cartItems")) || [];
            const newItem = {
                productId: productId,
                quantity: quantityValue,
                price: productPrice
            };
            cartItems.push(newItem);
            sessionStorage.setItem("cartItems", JSON.stringify(cartItems));
            console.log('cartItems', cartItems);

            // Enable cart button if there are items in the cart
            if (cartItems.length > 0) {
                cartButton.removeAttribute("disabled");
                cartButton.style.backgroundColor = "";
                cartButton.style.pointerEvents = "";
            }

            // Show SweetAlert2 notification after adding the product
            Swal.fire({
                icon: 'success',
                title: 'Товар добавлен в корзину',
                showConfirmButton: false,
                timer: 1500
            });
        });
    });
});