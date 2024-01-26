document.addEventListener("DOMContentLoaded", function () {
    const gridViewBtn = document.getElementById("gridViewBtn");
    const listViewBtn = document.getElementById("listViewBtn");
    const productContainer = document.getElementById("productsContainer"); // Используем ID

    gridViewBtn.addEventListener("click", function () {
        // Удалить класс "list-view" и добавить класс "grid-view"
        productContainer.classList.remove("list-view");
        productContainer.classList.add("grid-view");

        // Пройтись по всем элементам с id="productCard" и изменить их классы
        const productCards = document.querySelectorAll("#productCard");
        productCards.forEach((card) => {
            card.classList.remove("col-lg-12");
            card.classList.add("col-lg-4");
        });
    });

    listViewBtn.addEventListener("click", function () {
        // Удалить класс "grid-view" и добавить класс "list-view"
        productContainer.classList.remove("grid-view");
        productContainer.classList.add("list-view");

        // Пройтись по всем элементам с id="productCard" и изменить их классы
        const productCards = document.querySelectorAll("#productCard");
        productCards.forEach((card) => {
            card.classList.remove("col-lg-4");
            card.classList.add("col-lg-12");
        });
    });
});