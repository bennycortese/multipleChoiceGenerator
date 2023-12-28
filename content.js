console.log("YouTube Extension activated on this page.");

function fetchDataAndUpdateOverlay() {
    // Send a message to the background script to fetch data
    chrome.runtime.sendMessage({message: "fetchData"}, response => {
        if (response && response.data) {
            console.log('Data received from background:', response.data);
            // Now that you have data, call a function to update the overlay
            updateOverlayContent(response.data);
        } else {
            console.error('No data received');
        }
    });
}

function checkAnswer(selectedOption, correctAnswer) {
    // Getting all the option labels
    const optionLabels = document.querySelectorAll('label');
    
    // Resetting all option colors to default
    optionLabels.forEach(label => {
        label.style.backgroundColor = '#f9f9f9';
    });

    // Getting the parent label of the selected option
    let parentLabel = selectedOption.parentElement;

    // Check if the selected answer is correct
    if (selectedOption.value === correctAnswer) {
        // Change the color of the label to green for correct
        parentLabel.style.backgroundColor = 'lightgreen';
    } else {
        // Change the color of the label to red for incorrect
        parentLabel.style.backgroundColor = 'lightcoral';
    }
}

function setupOptionListeners() {
    const labels = document.querySelectorAll('.option-label');
    const radios = document.querySelectorAll('input[type=radio][name="option"]');

    radios.forEach(radio => {
        radio.addEventListener('change', () => {
            // Clear all labels' selected state
            labels.forEach(label => label.classList.remove('selected-label'));

            // If the current radio button is checked, add the class to its label
            if (radio.checked) {
                const parentLabel = radio.closest('.option-label');
                if (parentLabel) {
                    parentLabel.classList.add('selected-label');
                }
            }
        });
    });
}

function updateOverlayContent(data) {
    const videoPlayer = document.querySelector('.html5-video-player');
    const video = document.querySelector('video');
    const myData = data.split("-"); // NOTE FOR FUTURE - find a better delimiter because some questions may use '-' in the question
    console.log('I am here, here is the data:', data.split("")); 
    if (videoPlayer && video) {
        var link = document.createElement("link");
        link.href = chrome.runtime.getURL('styles.css');
        link.type = "text/css";
        link.rel = "stylesheet";
        document.getElementsByTagName("head")[0].appendChild(link);

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

        const safeTitle = escapeHTML(data);
        // Define the HTML content for the overlay
        const htmlContent = `
        <div class="overlay">
            <div class="content-box">
                <h2 class="title">1. ${escapeHTML(myData[1])}</h2>
                ${myData.slice(2, 6).map((option, index) => `
                <div class="option">
                    <label class="option-label" for="option${index}">
                        <input type="radio" id="option${index}" name="option" value="${['A', 'B', 'C', 'D'][index]}"/> <span> ${escapeHTML(option)} </span>
                    </label>
                </div>
                `).join('')}
                <button class="submit-btn">Click to Play/Pause</button>
            </div>
        </div>
        `;

        // Set the innerHTML of the overlay
        overlay.innerHTML = htmlContent;

        
        const correctFirstQuestionAnswer = escapeHTML(myData[6]);

            

        //document.querySelectorAll('input[type=radio][name="option"]').forEach(radio => {
        //    radio.addEventListener('change', function() {
        //        checkAnswer(this, correctFirstQuestionAnswer);
        //    });
        //});

        // Append the overlay to the video player
        videoPlayer.appendChild(overlay);

        setupOptionListeners();

        // Find the button in the overlay and add click event to play/pause video
        const button = overlay.querySelector('button');
        video.pause();
        //button.addEventListener('click', () => {
        //if (!video.paused) {
        //    button.innerText = 'Click to Play';
        //} else {
        //    button.innerText = 'Click to Pause';
        //}
        //});
             // Check every second
        }
  
}


window.addEventListener('load', () => {
    if(true) {
        const video = document.querySelector('video');
        if (video) {
            const targetTime = 30; // in seconds
            const checkTimeInterval = setInterval(() => {
                if (video.currentTime >= targetTime) {
                    clearInterval(checkTimeInterval);
                    fetchDataAndUpdateOverlay(); // Fetch data and update the overlay when the time is right
                }
            }, 1000); // Check every second
        }
    }
});

  

  function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag]));
}