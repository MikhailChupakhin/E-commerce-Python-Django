document.addEventListener("DOMContentLoaded", function () {
    const quantityControlsList = document.querySelectorAll('.quantity-controls');

    // Функция для пересчета стоимости
    function updateTotalPrice(input) {
        const productId = parseInt(input.getAttribute('data-product-id'));
        const quantity = parseInt(input.value);
        const price = parseFloat(input.getAttribute('data-product-price'));
        const totalPrice = quantity * price;
        const totalPriceElement = document.getElementById(`totalPrice_${productId}`);
        if (totalPriceElement) {
            console.log(`Updating total price element for product with id ${productId}`);
            totalPriceElement.textContent = totalPrice.toFixed(2) + ' р.'; // Предполагается, что стоимость округляется до двух знаков после запятой
        }
    }

    // Обработчик события после инициализации карусели
    function handleAfterMount(glideInstance) {
        const quantityInputs = glideInstance.slides.querySelectorAll('.quantity-input');
        quantityInputs.forEach(input => {
            const productId = parseInt(input.getAttribute('data-product-id'));
            updateTotalPrice(input);
            input.addEventListener('input', () => updateTotalPrice(input));
        });
    }


    // Инициализация каруселей
    const recommendedGlide = document.querySelector("#recommended_products .glide");
    if (recommendedGlide) {
        const glideInstance = new Glide(recommendedGlide, {
            type: "slider",
            perView: 4,
            focusAt: false,
            gap: 5,
            breakpoints: {
                768: {
                    perView: 2
                },
                480: {
                    perView: 1
                }
            }
        });

        glideInstance.on('afterMount', handleAfterMount); // Повесить обработчик после инициализации карусели
        glideInstance.mount();
    }

    const similarGlide = document.querySelector("#similar_products .glide");
    if (similarGlide) {
        const glideInstance = new Glide(similarGlide, {
            type: "slider",
            perView: 4,
            focusAt: false,
            gap: 5,
            breakpoints: {
                768: {
                    perView: 2
                },
                480: {
                    perView: 1
                }
            }
        });

        glideInstance.on('afterMount', handleAfterMount); // Повесить обработчик после инициализации карусели
        glideInstance.mount();
    }

    const viewedGlide = document.querySelector("#viewed_products .glide");
    if (viewedGlide) {
        const glideInstance = new Glide(viewedGlide, {
            type: "slider",
            perView: 4,
            focusAt: false,
            gap: 5,
            breakpoints: {
                768: {
                    perView: 2
                },
                480: {
                    perView: 1
                }
            }
        });

        glideInstance.on('afterMount', handleAfterMount); // Повесить обработчик после инициализации карусели
        glideInstance.mount();
    }

    function shouldShowControls(glideInstance) {
        const visibleSlides = glideInstance.settings.perView;
        const totalSlides = glideInstance._slides.length;

        console.log(`Visible Slides: ${visibleSlides}`);
        console.log(`Total Slides: ${totalSlides}`);

        return totalSlides > visibleSlides;
    }

    // Отслеживаем клики на кнопках "+" и "-"
    quantityControlsList.forEach(control => {
        const productId = parseInt(control.querySelector('.quantity-input').getAttribute('data-product-id'));
        const decreaseButton = control.querySelector('.quantity-decrease');
        const increaseButton = control.querySelector('.quantity-increase');
        const input = control.querySelector('.quantity-input');

        decreaseButton.addEventListener('click', function () {
            if (input.value > 1) {
                input.value = parseInt(input.value) - 1;
                updateTotalPrice(input);
            }
        });

        increaseButton.addEventListener('click', function () {
            input.value = parseInt(input.value) + 1;
            updateTotalPrice(input);
        });

        input.addEventListener('input', function () {
            updateTotalPrice(input);
        });
    });
});





