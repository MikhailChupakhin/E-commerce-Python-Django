$(document).ready(function() {
    // При клике на категорию (с классом .category-toggle)
    $('.category-toggle').click(function() {
        // Находим родительский элемент, содержащий подкатегории (с классом .subcategory-list)
        var subcategoryList = $(this).next('.subcategory-list');
        // Переключаем видимость подкатегорий
        subcategoryList.slideToggle();
    });
});