// Получите ссылку на главное изображение и на все дополнительные изображения
const mainImage = document.getElementById('mainImage');
const alterImages = document.querySelectorAll('.alter-image');

// Добавьте обработчик события клика к каждому дополнительному изображению
alterImages.forEach((alterImage) => {
    alterImage.addEventListener('click', () => {
        // Сохраните текущий и новый источники изображений
        const currentSrc = mainImage.src;
        const newSrc = alterImage.querySelector('img').src;

        // Обновите источники изображений
        mainImage.src = newSrc;
        alterImage.querySelector('img').src = currentSrc;
    });
});