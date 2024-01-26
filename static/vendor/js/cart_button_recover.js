document.addEventListener("DOMContentLoaded", function () {
    const cartItems = JSON.parse(sessionStorage.getItem("cartItems")) || [];
    const cartButton = document.getElementById("cartButton");

    // Если в корзине есть товары, кнопка становится активной
    if (cartItems.length > 0) {
        cartButton.removeAttribute("disabled");
        cartButton.style.backgroundColor = "";
        cartButton.style.pointerEvents = "";
    }
});
