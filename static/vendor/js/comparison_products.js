document.addEventListener("DOMContentLoaded", function () {
  const addToComparisonButtons = document.querySelectorAll('.comparison-container .add-to-comparison');
  addToComparisonButtons.forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.preventDefault();

      const link = this;
      const productId = parseInt(link.getAttribute('data-product-id'));
      const sessionId = link.getAttribute('data-session-id');
      const csrfToken = getCookie('csrftoken');

      addToComparison(productId, sessionId, csrfToken, link);
    });
  });

  function addToComparison(productId, sessionId, csrfToken, link) {
    console.log('Adding/removing product', productId, 'to/from comparison with session_id', sessionId);
    const data = {
      product_id: productId,
      session_id: sessionId
    };

    fetch(`/products/add_to_comparison/${productId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(data)
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(function (response) {
        console.log('Product added/removed to/from comparison successfully');

        const productCount = parseInt(response.product_count);

        if (productCount === 2 || productCount === 3) {
          showNotification('success', '', response.message, true);
        } else {
          showNotification('success', '', response.message, false);
        }

        link.classList.toggle('remove-from-comparison');
        link.classList.toggle('add-to-comparison');
        const iconElement = link.querySelector('i');
        iconElement.classList.toggle('lnr-sync');
        iconElement.classList.toggle('lnr-cross');

        if (link.classList.contains('remove-from-comparison')) {
          link.style.backgroundColor = 'darkred';
        } else {
          link.style.backgroundColor = '';
        }
      })
      .catch(function (error) {
        showNotification('error', '', 'Возможно сравнивать не более 3 товаров одновременно', false);
      });
  }

  function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
  }

  function showNotification(type, title, text, hasButtons) {
    let options = {
      icon: type,
      title: title,
      text: text,
      timer: hasButtons ? null : 1500,
      showConfirmButton: hasButtons,
      showCancelButton: hasButtons,
      confirmButtonText: "Перейти",
      cancelButtonText: "Закрыть"
    };

    Swal.fire(options).then(result => {
      if (!hasButtons && result.dismiss === Swal.DismissReason.timer) {
        // Уведомление было автоматически закрыто
        // Вместо этого вы можете выполнить другие действия при автоматическом закрытии
      } else if (hasButtons && result.isConfirmed) {
        window.location.href = 'https://imsound.ru/products/compare/';
      }
    });
  }
});