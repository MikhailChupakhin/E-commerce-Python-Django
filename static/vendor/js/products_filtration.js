document.addEventListener("DOMContentLoaded", function() {
    // Инициализация слайдера цены
    var priceSlider = document.getElementById("price-slider");

    var minPriceInput = document.getElementById("min_price");
    var maxPriceInput = document.getElementById("max_price");

    noUiSlider.create(priceSlider, {
        start: [parseInt(minPriceInput.value), parseInt(maxPriceInput.value)],
        connect: true,
        range: {
            'min': 0,
            'max': 1300000
        },
        step: 1
    });

    priceSlider.noUiSlider.on('update', function(values, handle) {
        minPriceInput.value = Math.round(values[0]);
        maxPriceInput.value = Math.round(values[1]);
    });

    // Устанавливаем aria-label для нижнего ползунка
    var lowerHandle = priceSlider.querySelector('.noUi-handle-lower');
    lowerHandle.setAttribute('aria-label', 'Нижний ползунок для выбора цены');

    // Устанавливаем aria-label для верхнего ползунка
    var upperHandle = priceSlider.querySelector('.noUi-handle-upper');
    upperHandle.setAttribute('aria-label', 'Верхний ползунок для выбора цены');

    // Функция для применения фильтров
    function applyFilters() {
        var minPrice = Math.round(minPriceInput.value);
        var maxPrice = Math.round(maxPriceInput.value);
        var inStock = document.getElementById("in_stock").checked ? "&in_stock=true" : "";
        var manufacturerCheckboxes = document.querySelectorAll("input[name='manufacturer[]']:checked");
        var manufacturers = Array.from(manufacturerCheckboxes).map(function(checkbox) {
            return checkbox.value;
        });

        var manufacturerParam = manufacturers.length > 0 ? "&manufacturer[]=" + manufacturers.join("&manufacturer[]=") : "";
        var currentPath = window.location.pathname;
        var url = window.location.origin + currentPath + "?min_price_value=" + minPrice +
          "&max_price_value=" + maxPrice + inStock + manufacturerParam;
        window.location.href = url;
    }

    // Применение фильтров при нажатии кнопки "Применить фильтр"
    document.getElementById("apply-filter-button").addEventListener("click", applyFilters);
});