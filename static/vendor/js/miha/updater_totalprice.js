async function updateTotalPrice(productId) {
    const input = document.getElementById(`quantity_${productId}`);
    const quantity = parseInt(input.value);
    const price = parseFloat(input.getAttribute('data-product-price'));
    const totalPrice = quantity * price;
    const totalPriceElement = document.getElementById(`totalPrice_${productId}`);
    totalPriceElement.textContent = totalPrice.toFixed(2) + ' р.';
}

const quantityInputs = document.querySelectorAll('.quantity-input');
quantityInputs.forEach(input => {
    const productId = input.closest('.card-body').getAttribute('data-product-id');
    updateTotalPrice(productId); // Вызываем функцию пересчета сразу для начальных значений
    input.addEventListener('input', async () => {
        await updateTotalPrice(productId);
    });
});