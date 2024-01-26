document.addEventListener("DOMContentLoaded", function () {
    const addToCartButtonsNoAuth = document.querySelectorAll(".add-to-cart-noauth");
    const cartButton = document.getElementById("cartButton");

    addToCartButtonsNoAuth.forEach(function (button) {
        button.addEventListener("click", function (event) {
            const button = event.target;
            const productId = button.getAttribute("data-product-id");
            const productName = button.getAttribute("data-product-name");

            // Найти ближайший элемент с классом "product-inner"
            const productInnerElement = button.closest(".product-inner");

            // Получить значение цены из элемента с классом "total-price"
            const priceElement = productInnerElement.querySelector(`#totalPrice_${productId}`);
            const productPrice = priceElement ? parseFloat(priceElement.getAttribute("data-product-price")) : 0;

            // Получить значение количества из input с id, содержащим productId
            const quantityInput = productInnerElement.querySelector(`#quantity_${productId}`);
            const quantityValue = quantityInput ? parseInt(quantityInput.value) : 1;


            // Вывести значения для проверки
            console.log("Product ID:", productId);
            console.log("Product Name:", productName);
            console.log("Product Price:", productPrice);
            console.log("Quantity:", quantityValue);

            // Обновление sessionStorage после добавления товара
            const cartItems = JSON.parse(sessionStorage.getItem("cartItems")) || []; // Получаем текущий список или создаём новый, если пусто
            const newItem = {
                productId: productId,
                productName: productName,
                quantity: quantityValue,
                price: productPrice
            };
            cartItems.push(newItem);
            sessionStorage.setItem("cartItems", JSON.stringify(cartItems));

            // После добавления товара в sessionStorage
            console.log('cartItems', cartItems);

            // Если в корзине есть товары, сделайте кнопку активной
            if (cartItems.length > 0) {
                cartButton.removeAttribute("disabled");
                cartButton.style.backgroundColor = "";
                cartButton.style.pointerEvents = "";
            }

            // Показать уведомление SweetAlert2 после добавления товара
            Swal.fire({
                icon: 'success',
                title: 'Товар добавлен в корзину',
                showConfirmButton: false,
                timer: 1500
            });
        });
    });
});