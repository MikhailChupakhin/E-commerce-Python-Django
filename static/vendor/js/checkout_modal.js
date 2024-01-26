document.addEventListener("DOMContentLoaded", function () {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const checkoutButton = document.getElementById("checkout-button");
    const checkoutModal = document.getElementById("checkout-modal");
    const closeModal = checkoutModal.querySelector(".close");
    const createOrderButton = checkoutModal.querySelector("#create-order-btn");

    checkoutButton.addEventListener("click", function () {
        checkoutModal.style.display = "block";
    });

    closeModal.addEventListener("click", function () {
        checkoutModal.style.display = "none";
    });

    createOrderButton.addEventListener("click", function (event) {
        event.preventDefault();

        // Собрать данные для заказа из полей формы
        const name = document.getElementById("name").value;
        const phone = document.getElementById("phone").value;
        const email = document.getElementById("email").value;
        const address = document.getElementById("address").value;

        // Собрать данные о товарах из sessionStorage
        const cartItems = JSON.parse(sessionStorage.getItem("cartItems")) || [];

        // Создать объект FormData и добавьте в него CSRF-токен
        const formData = new FormData();
        formData.append("csrfmiddlewaretoken", csrfToken);
        formData.append("name", name);
        formData.append("phone", phone);
        formData.append("email", email);
        formData.append("address", address);
        formData.append("cartItems", JSON.stringify(cartItems));

        fetch("https://imsound.ru/orders/order-create-noauth/", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Обработать ответ от сервера, например, показать сообщение об успешном заказе
            console.log(data.message);
            checkoutModal.style.display = "none";
        })
        .catch(error => {
            console.error("Error creating order:", error);
        });
    });
});