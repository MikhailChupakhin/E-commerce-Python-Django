$(document).ready(function () {
    var loadMoreButton = $("#load-more-button");
    var offset = 9;

    loadMoreButton.on("click", function (e) {
        e.preventDefault();

        let url;
        url = '/blog/load-more-posts/';
        $.ajax({
            url: url,
            data: { offset: offset },
            success: function (data) {
                console.log(data);
                if (data.html) {
                    $(".blog .row").append(data.html);
                    offset += 9;
                } else {
                    loadMoreButton.hide();
                }
            }
        });
    });
});