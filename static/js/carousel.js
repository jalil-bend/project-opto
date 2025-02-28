let slideIndex = 0;

function showSlides() {
    const slides = document.querySelectorAll(".testimonial-slide");
    slides.forEach(slide => slide.classList.remove("active"));
    slideIndex = (slideIndex + 1) % slides.length;
    slides[slideIndex].classList.add("active");
    setTimeout(showSlides, 5000);
}

document.addEventListener("DOMContentLoaded", showSlides);
