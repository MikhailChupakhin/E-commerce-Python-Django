$(document).ready(function() {
  // Находим все дополнительные изображения
  var additionalImages = $(".additional__image");

  // Обрабатываем клик по дополнительным изображениям
  additionalImages.click(function() {
    // Получаем URL выбранного дополнительного изображения
    var newImageUrl = $(this).attr("src");

    // Получаем текущий URL основного изображения
    var mainImageUrl = $(".main__image").attr("src");

    // Заменяем URL основного изображения на URL выбранного дополнительного изображения
    $(".main__image").attr("src", newImageUrl);

    // Заменяем URL выбранного дополнительного изображения на URL предыдущего основного изображения
    $(this).attr("src", mainImageUrl);
  });
});
