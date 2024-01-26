document.addEventListener("DOMContentLoaded", function () {
    const cartItemsContainer = document.getElementById("cart-items");

    // Получение данных из sessionStorage и создание таблицы
    const cartItems = JSON.parse(sessionStorage.getItem("cartItems")) || [];

    if (cartItems.length > 0) {
        const table = document.createElement("table");
        table.classList.add("table"); // Добавляем класс для стилизации Bootstrap

        // Создаем заголовок таблицы
        const headerRow = document.createElement("tr");
        headerRow.innerHTML = `
            <th scope="col">Товар</th>
            <th scope="col">Количество</th>
            <th scope="col">Цена</th>
        `;
        table.appendChild(headerRow);

        // Создаем строки таблицы для каждого товара
        cartItems.forEach(function (item) {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${item.productName}</td>
                <td>${item.quantity}</td>
                <td>${item.price}</td>
            `;
            table.appendChild(row);
        });

        cartItemsContainer.appendChild(table);
    } else {
        cartItemsContainer.innerHTML = "Корзина пуста.";
    }
});