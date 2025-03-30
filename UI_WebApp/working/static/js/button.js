let imageArray = [];
let visibleImages = []; // Stores the current 5 images
let hiddenImages = []; // Stores the remaining images
let currentImage = null; // The currently displayed image

document.addEventListener("DOMContentLoaded", async () => {
    const imageLinksContainer = document.getElementById("imageLinks");
    const displayedImage = document.getElementById("displayedImage"); // Ensure it's an <img> tag
    const removeButton = document.getElementById("removeButton");

    async function fetchImages() {
        try {
            const response = await fetch('/get-images'); // Fetch list of images from Flask server
            if (!response.ok) throw new Error("Failed to fetch images");

            const images = await response.json(); // Parse JSON response
            imageArray = images.map(file => `static/data/${file}`); // Populate global array
            hiddenImages = [...imageArray]; // Fill hidden images

            console.log("Fetched images:", imageArray);
            initializeLinks(); // Initialize UI after fetching images
        } catch (error) {
            console.error("Error fetching images:", error);
        }
    }

    function initializeLinks() {
        visibleImages = hiddenImages.splice(0, 5); // Take first 5 images
        renderLinks();
    }

    function renderLinks() {
        imageLinksContainer.innerHTML = ""; // Clear previous links
        visibleImages.forEach((image, index) => {
            const link = document.createElement("a");
            link.href = "#";
            link.textContent = `Object ${index + 1}`;
            link.classList.add("image-link");
            link.addEventListener("click", () => showImage(image, index));
            imageLinksContainer.appendChild(link);
        });
    }

    function showImage(imageSrc, index) {
        displayedImage.src = imageSrc;
        displayedImage.style.display = "block";
        removeButton.style.display = "inline-block";
        currentImage = index;
    }

    removeButton.addEventListener("click", async function () {
        if (currentImage !== null) {
            const imageToDelete = visibleImages[currentImage];
    
            try {
                const response = await fetch('/delete-image', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: imageToDelete.split('/').pop() }) // Send only the filename
                });
    
                if (!response.ok) throw new Error("Failed to delete image");
    
                visibleImages.splice(currentImage, 1); // Remove from visible images
                if (hiddenImages.length > 0) {
                    visibleImages.push(hiddenImages.shift()); // Replace with another if available
                }
    
                displayedImage.style.display = "none";
                removeButton.style.display = "none";
                renderLinks();
            } catch (error) {
                console.error("Error deleting image:", error);
            }
        }
    });
    

    await fetchImages(); // Fetch images and initialize UI
});
