console.log("YouTube Extension activated on this page.");

window.addEventListener('load', () => {
  const videoPlayer = document.querySelector('.html5-video-player');
  const video = document.querySelector('video');

  if (videoPlayer && video) {
    const overlay = document.createElement('div');
    overlay.style.position = 'absolute';
    overlay.style.zIndex = '1000';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.display = 'flex';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.style.backgroundColor = 'rgba(0,0,0,0.75)'; // Darker semi-transparent background

    // Define the HTML content for the overlay
    const htmlContent = `
    <div style="width: 80%; max-width: 500px; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
      <h2 style="color: #333; font-size: 24px; text-align: center; margin-bottom: 20px;">1. What is the capital of France?</h2>
      <div style="margin-bottom: 10px;">
        <label style="cursor: pointer; display: block; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
          <input type="radio" name="option" value="A" style="margin-right: 10px;"/> <span style="color: #333;"> A) London </span>
        </label>
      </div>
      <div style="margin-bottom: 10px;">
        <label style="cursor: pointer; display: block; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
          <input type="radio" name="option" value="B" style="margin-right: 10px;"/> <span style="color: #333;"> B) Paris </span>
        </label>
      </div>
      <div style="margin-bottom: 10px;">
        <label style="cursor: pointer; display: block; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
          <input type="radio" name="option" value="C" style="margin-right: 10px;"/> <span style="color: #333;"> C) Berlin </span>
        </label>
      </div>
      <div style="margin-bottom: 20px;">
        <label style="cursor: pointer; display: block; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
          <input type="radio" name="option" value="D" style="margin-right: 10px;"/> <span style="color: #333;">D) Madrid</span>
        </label>
      </div>
      <button style="width: 100%; padding: 10px 20px; background-color: #3490dc; color: white; border: none; border-radius: 5px; cursor: pointer;">Click to Play/Pause</button>
    </div>
    `;

    // Set the innerHTML of the overlay
    overlay.innerHTML = htmlContent;

    // Append the overlay to the video player
    videoPlayer.appendChild(overlay);

    // Find the button in the overlay and add click event to play/pause video
    const button = overlay.querySelector('button');
    button.addEventListener('click', () => {
      if (!video.paused) {
        video.pause();
        button.innerText = 'Click to Play';
      } else {
        video.play();
        button.innerText = 'Click to Pause';
      }
    });
  }
});
