$(document).ready(function() {
    var comparisonProductIds = $('#comparison-product-ids').val();
    if (comparisonProductIds) {
        try {
            comparisonProductIds = JSON.parse(comparisonProductIds);

            $('.add-to-comparison').each(function() {
                var productId = $(this).data('product-id');
                if (comparisonProductIds.includes(productId)) {
                    $(this).addClass('remove-from-comparison');
                    $(this).find('i').removeClass('lnr-heart').addClass('lnr-cross');
                    $(this).css('background-color', 'darkred');
                }
            });
        } catch (error) {
            // Обработка ошибки при разборе JSON
            console.error('Error parsing JSON:', error);
        }
    }
});