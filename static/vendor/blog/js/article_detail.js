document.addEventListener("DOMContentLoaded", function () {
    const leaveCommentBtn = document.querySelector(".leave-btn");
    const commentForm = document.getElementById("comment-form");
    const commentText = document.getElementById("comment-text");
    const submitCommentBtn = document.getElementById("submit-comment");

    commentForm.classList.add("hidden-form");

    leaveCommentBtn.addEventListener("click", function (e) {
        e.preventDefault();
        const domainName = "http://127.0.0.1:8000";
        const userId = leaveCommentBtn.getAttribute("data-user-id");

        const isAuthenticated = userId !== "None";
        if (isAuthenticated) {
            commentForm.classList.toggle("hidden-form");
        } else {
            window.location.href = `${domainName}/users/login/`;
        }
    });

    submitCommentBtn.addEventListener("click", function () {
        const commentTextValue = commentText.value;

        if (commentTextValue.trim() !== '') {
            const domainName = "http://127.0.0.1:8000";
            const userId = leaveCommentBtn.getAttribute("data-user-id");
            const articleId = leaveCommentBtn.getAttribute("data-article-id");
            const csrfToken = getCookie('csrftoken');

            const data = {
                user_id: userId,
                text: commentTextValue,
                article_id: articleId,
                csrfmiddlewaretoken: csrfToken
            };

            fetch(`${domainName}/reviews/create_comment/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Что-то пошло не так при отправке комментария.');
                }
            })
            .then(responseData => {
                Swal.fire({
                    icon: 'success',
                    title: 'Комментарий отправлен на модерацию',
                    text: 'Ваш комментарий будет опубликован после проверки.',
                });
                commentText.value = ''; // Очищаем текстовое поле комментария
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: 'Ошибка',
                    text: error.message,
                });
            });
        }
    });

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});