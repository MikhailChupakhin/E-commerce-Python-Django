document.addEventListener('DOMContentLoaded', function () {
    const clearComparisonButton = document.getElementById('clearComparison');

    clearComparisonButton.addEventListener('click', function () {
        var url = 'https://imsound.ru/products/clear_comparison/'
        var request_url = 'https://imsound.ru/products'
        const csrftoken = getCookie('csrftoken');
        // Отправляем fetch запрос на сервер для удаления списка сравнения
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
        })
        .then(response => {
            if (response.ok) {
                window.location.href = request_url;
            } else {
                console.error('Ошибка при очистке списка сравнения');
            }
        })
        .catch(error => {
            console.error('Произошла ошибка при выполнении запроса:', error);
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}