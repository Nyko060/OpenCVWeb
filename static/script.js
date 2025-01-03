const videoElement = document.getElementById("videoElement");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

// Mostrar el video procesado del backend
const videoFeed = document.createElement("img");
videoFeed.src = "/video_feed";
videoFeed.style.display = "none"; // No mostramos la etiqueta <img> directamente

videoFeed.onload = () => {
    canvas.width = videoFeed.width;
    canvas.height = videoFeed.height;

    function draw() {
        context.drawImage(videoFeed, 0, 0, canvas.width, canvas.height);
        requestAnimationFrame(draw);
    }

    draw();
};
