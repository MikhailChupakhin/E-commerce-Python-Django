function updateTotalPrice(productId) {
    const input = document.getElementById(`quantity_${productId}`);
    const quantity = parseInt(input.value);
    const priceElement = input.closest('.product-inner').querySelector('.total-price');
    const price = parseFloat(priceElement.getAttribute('data-product-price'));
    const totalPrice = quantity * price;
    priceElement.textContent = totalPrice.toFixed(2);
}

window.onload = function () {
    const productContainers = document.querySelectorAll('.product-inner');

    productContainers.forEach(container => {
        const productId = parseInt(container.querySelector('.quantity-input').getAttribute('data-product-id'));
        const decreaseButton = container.querySelector('.quantity-btn.decrease');
        const increaseButton = container.querySelector('.quantity-btn.increase');
        const input = container.querySelector('.quantity-input');

        decreaseButton.addEventListener('click', function () {
            if (input.value > 1) {
                input.value = parseInt(input.value) - 1;
                updateTotalPrice(productId);
                console.log(`Decrease button clicked for product ${productId}. New quantity: ${input.value}`);
            }
        });

        increaseButton.addEventListener('click', function () {
            input.value = parseInt(input.value) + 1;
            updateTotalPrice(productId);
            console.log(`Increase button clicked for product ${productId}. New quantity: ${input.value}`);
        });

        input.addEventListener('input', function () {
            updateTotalPrice(productId);
            console.log(`Input changed for product ${productId}. New quantity: ${input.value}`);
        });

        // Вызываем функцию пересчета сразу для начальных значений
        updateTotalPrice(productId);
    });
}