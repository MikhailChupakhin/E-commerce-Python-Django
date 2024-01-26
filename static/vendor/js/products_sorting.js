const form = document.getElementById("products_sorting_form");
const select = document.getElementById("sort-select");

form.addEventListener("submit", function(event) {
    event.preventDefault();

    const selectedOption = select.options[select.selectedIndex];
    const selectedSortValue = selectedOption.value;

    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set("sort", selectedSortValue);

    window.location.href = currentUrl.toString();
});
