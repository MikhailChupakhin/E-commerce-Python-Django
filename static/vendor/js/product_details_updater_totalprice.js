window.onload = function () {
    const quantityContainers = document.querySelectorAll('.quantity-input-container');

    quantityContainers.forEach(container => {
        const productId = parseInt(container.querySelector('.quantity-input').getAttribute('data-product-id'));
        const cardType = container.getAttribute('data-card-type');
        const decreaseButton = container.querySelector('.quantity-btn.decrease');
        const increaseButton = container.querySelector('.quantity-btn.increase');
        const input = container.querySelector('.quantity-input');

        increaseButton.addEventListener('click', function () {
            input.value = parseInt(input.value) + 1;
            updateTotalPrice(productId, cardType);

            // Проверяем тип карточки и управляем видимостью соответствующих элементов
            if (cardType === 'main') {
                const totalMain = document.querySelector(`.total-price-section-main`);
                // Установить видимость элемента как видимый
                totalMain.style.visibility = 'visible';
            } else if (cardType === 'additional') {
                const priceSection = container.closest('.price-section');
                const totalPriceSection = priceSection.querySelector('.total-price-section');
                totalPriceSection.classList.remove('hidden');
            }
        });

        decreaseButton.addEventListener('click', function () {
            if (input.value > 1) {
                input.value = parseInt(input.value) - 1;
                updateTotalPrice(productId);
            }
        });

        input.addEventListener('input', function () {
            updateTotalPrice(productId);
        });

        // Вызываем функцию пересчета сразу для начальных значений
        updateTotalPrice(productId);
    });
}

function updateTotalPrice(productId) {
    const input = document.getElementById(`quantity_${productId}`);
    const quantity = parseInt(input.value);
    const priceElement = document.querySelector(`#totalPrice_${productId}`);
    const price = parseFloat(priceElement.getAttribute('data-product-price'));
    const totalPrice = quantity * price;
    priceElement.textContent = totalPrice.toFixed(2);
}