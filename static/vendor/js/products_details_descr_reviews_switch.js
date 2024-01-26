function toggleSection(section) {
    const descriptionSection = document.getElementById('description');
    const reviewsSection = document.getElementById('reviews');
    const descriptionButton = document.querySelector('[data-section="description"]');
    const reviewsButton = document.querySelector('[data-section="reviews"]');

    if (section === 'description') {
        descriptionSection.style.display = 'block';
        reviewsSection.style.display = 'none';
        descriptionButton.classList.add('active');
        reviewsButton.classList.remove('active');
    } else if (section === 'reviews') {
        descriptionSection.style.display = 'none';
        reviewsSection.style.display = 'block';
        descriptionButton.classList.remove('active');
        reviewsButton.classList.add('active');
    }
}