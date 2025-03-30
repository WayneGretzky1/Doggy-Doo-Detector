// Array of 10 images (Replace these with actual image URLs)
const imageArray = [
    "/static/img/blegen.jpg", "/static/img/Anderson.jpg", "/static/img/breakfast.jpg", "/static/img/bruininks.jpg", "/static/img/coffman.jpg",
    "/static/img/blegen.jpg", "/static/img/Anderson.jpg", "/static/img/breakfast.jpg", "/static/img/bruininks.jpg", "/static/img/coffman.jpg"
];

let visibleImages = []; // Stores the current 5 images
let hiddenImages = [...imageArray]; // Stores the remaining images
let currentImage = null; // The currently displayed image

document.addEventListener("DOMContentLoaded", () => {
    const imageLinksContainer = document.getElementById("imageLinks");
    const displayedImage = document.getElementById("displayedImage");
    const removeButton = document.getElementById("removeButton");

    // Function to initialize the first 5 images as links
    function initializeLinks() {
        while (visibleImages.length < 5 && hiddenImages.length > 0) {
            visibleImages.push(hiddenImages.shift());
        }
        renderLinks();
    }

    // Function to update the displayed links
    function renderLinks() {
        imageLinksContainer.innerHTML = "";
        visibleImages.forEach((image, index) => {
            const link = document.createElement("a");
            link.href = "#";
            link.textContent = `Object ${index + 1}`;
            link.classList.add("image-link");
            link.addEventListener("click", () => showImage(image, index));
            imageLinksContainer.appendChild(link);
        });
    }

    // Function to show the clicked image
    function showImage(imageSrc, index) {
        displayedImage.src = imageSrc;
        displayedImage.style.display = "block";
        removeButton.style.display = "inline-block";
        currentImage = index; // Store the index of the image being displayed
    }

    // Function to remove the displayed image and replace it with another one
    removeButton.addEventListener("click", function () {
        if (currentImage !== null) {
            visibleImages.splice(currentImage, 1); // Remove from visible images
            if (hiddenImages.length > 0) {
                visibleImages.push(hiddenImages.shift()); // Add a new one if available
            }
            displayedImage.style.display = "none";
            removeButton.style.display = "none";
            renderLinks();
        }
    });

    // Initialize the first set of links
    initializeLinks();
});
