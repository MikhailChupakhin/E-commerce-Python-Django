$(document).ready(function () {
    const modal = $("#quickviewModal");
    const modalTitle = modal.find(".modal-title");
    const modalPrice = modal.find("#modalPrice");
    const modalDescription = modal.find("#modalDescription");
    const modalImage = modal.find("#modalImage");

    $(".quick-view-btn").click(function (event) {
        event.preventDefault();
        const productId = $(this).data("product-id");
        const productName = $(this).data("product-name");
        const productPrice = $(this).data("product-price");
        const productImage = $(this).data("product-image");
        const productDescription = $(this).data("product-description");

        const productCharacteristicsArray = $(this).data("product-characteristics");

        modalTitle.text(productName);
        if (productPrice === '1000000,00') {
            modalPrice.text("ПО ЗАПРОСУ");
        } else {
            modalPrice.text(productPrice);
        }
        modalImage.attr("src", productImage);

        if (productDescription !== 'None' && productDescription !== undefined && productDescription !== "") {
            modalDescription.html("<strong>Описание:</strong><br>" + productDescription);
        } else {
            modalDescription.html("<strong>Описание:</strong><br>Товару пока не добавлено описание");
        }

        const characteristicsContainer = modal.find("#characteristicsContainer");
        characteristicsContainer.empty();

        if (productCharacteristicsArray.length > 0) {
            const table = $("<table>");
            table.addClass("table");
            const tableBody = $("<tbody>");

            for (const characteristic of productCharacteristicsArray) {
                const row = $("<tr>");
                const nameCell = $("<td>").text(characteristic.name);
                const valueCell = $("<td>").text(characteristic.value);

                row.append(nameCell, valueCell);
                tableBody.append(row);
            }

            table.append(tableBody);
            characteristicsContainer.append(table);
        } else {
            characteristicsContainer.html("Товару не добавлены характеристики");
        }
    });
});