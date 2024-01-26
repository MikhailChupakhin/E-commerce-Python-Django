$(document).ready(function() {
  var removedItems = []; // Массив для хранения информации о удаленных товарах

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function updateItem(parentContainer, isRemoved) {
    var itemId = parentContainer.data('item-id');
    if (isRemoved) {
      // Восстановление товара
      parentContainer.removeClass('removed');
      parentContainer.css({
        'background-color': 'transparent',
        'pointer-events': 'auto'
      });
      // Удаление информации о товаре из массива removedItems
      removedItems = removedItems.filter(function(item) {
        return item !== itemId;
      });
    } else {
      // Удаление товара
      parentContainer.addClass('removed');
      parentContainer.css({
        'background-color': 'rgba(0, 0, 0, 0.5)',
        'pointer-events': 'none'
      });
      // Добавление информации о товаре в массив removedItems
      removedItems.push(itemId);
    }
  }

    function isQuantityChanged() {
    var isChanged = false;
    $('input[name="basketID"]').each(function() {
      var newQuantity = parseInt($(this).val());
      var originalQuantity = parseInt($(this).data('quantity'));
      if (newQuantity !== originalQuantity) {
        isChanged = true;
        return false; // Прервать цикл
      }
    });
    return isChanged;
  }


  function saveChanges() {
    // Проверка, что есть удаленные товары или изменения в количестве
    if (removedItems.length > 0 || isQuantityChanged()) {
      var csrfToken = getCookie('csrftoken');
      var postData = {
        removed_items: removedItems,
        csrfmiddlewaretoken: csrfToken
      };

      // Получить все измененные значения количества товаров и добавить в postData
      $('input[name="basketID"]').each(function() {
        var itemId = $(this).closest('.card').data('item-id');
        var quantity = $(this).val();
        postData['quantity_' + itemId] = quantity;
      });

      $.ajax({
        url: '/products/baskets/update/',
        type: 'POST',
        dataType: 'json',
        data: postData,
        cache: false,
        success: function(response) {
          console.log(response.message);
          // Обработка успешного выполнения AJAX-запроса

          // Очистка массива удаленных товаров
          removedItems = [];
          // Обновление содержимого корзины на странице
          // $('.baskets-container').load(window.location.href + ' .baskets-container');
          window.location.reload();
        },
        error: function(xhr, status, error) {
          console.error(error);
        }
      }).done(function() {
        return false; // Предотвращение выполнения действия по умолчанию ссылки
      });
    } else {
      // Если нет удаленных товаров и нет изменений в количестве, выполните другие действия
    }
  }


  $('.remove-btn').on('click', function(event) {
    event.preventDefault();
    var parentContainer = $(this).closest('.card');
    var isRemoved = parentContainer.hasClass('removed');
    updateItem(parentContainer, isRemoved);
    console.log(removedItems);
  });


  $('a#save-btn').on('click', function(event) {
    event.preventDefault();
    saveChanges();
  });
});