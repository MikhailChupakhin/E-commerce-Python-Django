$(document).ready(function() {
  var defaultMinPrice = 500;
  var defaultMaxPrice = 100000;

  // Инициализируем слайдер цен
  $("#price-slider").slider({
    range: true,
    min: 0,
    max: 100000,
    values: [defaultMinPrice, defaultMaxPrice],
    slide: function(event, ui) {
      $("#min_price").val(ui.values[0]);
      $("#max_price").val(ui.values[1]);
      updateFilterUrl();
    }
  });

  // Функция для обновления URL при изменении фильтров
  function updateFilterUrl() {
    var minPrice = parseFloat($("#min_price").val());
    var maxPrice = parseFloat($("#max_price").val());
    var inStock = $("#in_stock").prop("checked");
    var selectedManufacturers = $(".manufacturer-checkbox:checked").map(function() {
      return $(this).val();
    }).get().join(',');

    var url = "/products/filter/?min_price=" + minPrice + "&max_price=" + maxPrice;

    if (selectedManufacturers) {
      url += "&manufacturer=" + selectedManufacturers;
    }

    if (inStock) {
      url += "&in_stock=on";
    }

    window.history.replaceState({}, '', url);
  }

  // Обработчик для изменения цены "От:"
  $("#min_price").on("change", function() {
    var minPrice = parseFloat($("#min_price").val());
    var maxPrice = parseFloat($("#max_price").val());

    if (minPrice < 0 || minPrice >= maxPrice) {
      $("#min_price").val(Math.max(minPrice, 0));
      minPrice = Math.max(minPrice, 0);
    }

    if (minPrice > maxPrice) {
      $("#max_price").val(minPrice);
      maxPrice = minPrice;
    }

    $("#price-slider").slider("values", 0, minPrice);

    updateFilterUrl();
  });

  // Обработчик для изменения цены "До:"
  $("#max_price").on("change", function() {
    var minPrice = parseFloat($("#min_price").val());
    var maxPrice = parseFloat($("#max_price").val());

    if (maxPrice < 0 || maxPrice <= minPrice) {
      $("#max_price").val(Math.max(maxPrice, 0));
      maxPrice = Math.max(maxPrice, 0);
    }

    if (maxPrice < minPrice) {
      $("#min_price").val(maxPrice);
      minPrice = maxPrice;
    }

    $("#price-slider").slider("values", 1, maxPrice);

    updateFilterUrl();
  });

  // Обработчик для изменения чекбокса "Только в наличии"
  $("#in_stock").on("change", function() {
    updateFilterUrl();
  });

  // Обработчик для изменения чекбоксов производителей
  $(".manufacturer-checkbox").on("change", function() {
    updateFilterUrl();
  });

  // Установка значений по умолчанию для цен
  $("#min_price").val(defaultMinPrice);
  $("#max_price").val(defaultMaxPrice);
});