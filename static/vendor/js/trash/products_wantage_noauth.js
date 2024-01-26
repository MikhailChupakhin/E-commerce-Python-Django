$(document).ready(function () {
    // Обработчик нажатия на кнопку "Оформить заказ"
    $("#order-btn").click(function (e) {
        e.preventDefault();
       // Получение данных из sessionStorage и создание таблицы
       const cartItems = JSON.parse(sessionStorage.getItem("cartItems")) || [];
       console.log("cartItems:", cartItems);

        // Добавляем CSRF токен к данным запроса
        var csrfToken = $('[name=csrfmiddlewaretoken]').val();

        $.ajax({
            url: '/orders/check_inventory_noauth/',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {items: JSON.stringify(cartItems)},
            success: function (response) {
                var unavailableProducts = response.unavailable_products;

                if (unavailableProducts.length > 0) {
                    // Если есть недоступные товары, покажите модальное окно
                    var tableContainer = $("#unavailable-products-table");
                    tableContainer.empty();

                    // Создаем таблицу с недоступными товарами
                    var table = $("<table>").addClass("table table-bordered");
                    var tableHead = $("<thead>").append($("<tr>").append($("<th>").text("Товар"), $("<th>").text("В корзине"), $("<th>").text("Доступно")));
                    var tableBody = $("<tbody>");
                    for (var i = 0; i < unavailableProducts.length; i++) {
                        var product = unavailableProducts[i];
                        var row = $("<tr>").append($("<td>").text(product.product_name),
                                                   $("<td>").text(product.basket_quantity),
                                                   $("<td>").text(product.available_quantity));
                        tableBody.append(row);
                    }
                    table.append(tableHead, tableBody);
                    tableContainer.append(table);

                    $("#stock-check-modal").modal("show");
                } else {
                    // Если все товары доступны, перенаправьте пользователя на страницу оформления заказа
                    $("#checkout-modal").modal("show");  // Показать модальное окно
                }
            },
            error: function (xhr, status, error) {
                // Обработка ошибки (если не удалось выполнить AJAX запрос)
                console.error(error);
            }
        });
    });

    // Обработчик нажатия на кнопку "Понятно" (confirmButton) вне блока AJAX-запроса
    $("#confirmButton").click(function () {
        $("#stock-check-modal").modal("hide");
    });

    // Обработчик нажатия на кнопку "Закрыть" (closeButton) вне блока AJAX-запроса
    $("#closeButton").click(function () {
        $("#stock-check-modal").modal("hide");
    });
});