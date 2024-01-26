document.addEventListener('DOMContentLoaded', function() {
    const applyCouponButton = document.getElementById('apply_coupon_button');
    const couponInput = document.querySelector('.coupon_input');
    
    applyCouponButton.addEventListener('click', function(event) {
        event.preventDefault();
        
        const promoCode = couponInput.value;
        console.log(promoCode)

        fetch('http://127.0.0.1:8000/users/apply_promo_code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFTokenFromCookie()
            },
            body: JSON.stringify({ promo_code: promoCode })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: 'Успех!',
                    text: 'Промо-код успешно применен. Скидка: ' + data.discount,
                    icon: 'success',
                    timer: 2000, // Уведомление исчезнет через 2 секунды
                    showConfirmButton: false
                });
                // Обновите информацию на странице, если это необходимо
            } else {
                Swal.fire({
                    title: 'Ошибка!',
                    text: 'Ошибка: ' + data.error,
                    icon: 'error',
                    timer: 2000, // Уведомление исчезнет через 2 секунды
                    showConfirmButton: false
                });
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    });

    function getCSRFTokenFromCookie() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            .split('=')[1];
        return cookieValue;
    }
});

