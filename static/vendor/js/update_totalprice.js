function updateTotalPrice(productId, isGrid) {
    const input = document.getElementById(`quantity_${productId}${isGrid ? '' : '-list'}`);
    const quantity = parseInt(input.value);
    const priceElement = input.closest('.product-inner').querySelector('.total-price');
    const price = parseFloat(priceElement.getAttribute('data-product-price'));
    const totalPrice = quantity * price;
    priceElement.textContent = totalPrice.toFixed(2);
}

window.onload = function () {
    const productContainers = document.querySelectorAll('.product-inner:not(.no_price)');

    productContainers.forEach(container => {
        const productId = parseInt(container.querySelector('.quantity-input').getAttribute('data-product-id'));
        const decreaseButton = container.querySelector('.quantity-btn.decrease');
        const increaseButton = container.querySelector('.quantity-btn.increase');
        const input = container.querySelector('.quantity-input');
        const isGrid = container.querySelector('.grid-mode');

        decreaseButton.addEventListener('click', function () {
            if (input.value > 1) {
                input.value = parseInt(input.value) - 1;
                updateTotalPrice(productId, isGrid);
                console.log(`Decrease button clicked for product ${productId}. New quantity: ${input.value}`);
            }
        });

        increaseButton.addEventListener('click', function () {
            input.value = parseInt(input.value) + 1;
            updateTotalPrice(productId, isGrid);
            console.log(`Increase button clicked for product ${productId}. New quantity: ${input.value}`);
        });

        input.addEventListener('input', function () {
            updateTotalPrice(productId, isGrid);
            console.log(`Input changed for product ${productId}. New quantity: ${input.value}`);
        });

        // Вызываем функцию пересчета сразу для начальных значений
        updateTotalPrice(productId, isGrid);
    });
}