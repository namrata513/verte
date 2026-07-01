document.addEventListener('DOMContentLoaded', () => {
    let currentSlideIndex = 0;
    let isScrollingLocked = false;
    const slides = document.querySelectorAll('.slide');
    
    // 2. Unified Slide Transition Logic
    window.updateSlides = function(nextIndex) {
        if (nextIndex < 0 || nextIndex >= slides.length) return;
        
        slides.forEach((slide, idx) => {
            slide.classList.remove('visible', 'invisible', 'opacity-100', 'opacity-0', 'translate-y-0', '-translate-y-full', 'translate-y-full');
            
            if (idx === nextIndex) {
                slide.classList.add('visible', 'opacity-100', 'translate-y-0');
                slide.style.pointerEvents = 'auto';
            } else if (idx < nextIndex) {
                slide.classList.add('invisible', 'opacity-0', '-translate-y-full');
                slide.style.pointerEvents = 'none';
            } else {
                slide.classList.add('invisible', 'opacity-0', 'translate-y-full');
                slide.style.pointerEvents = 'none';
            }
        });
        currentSlideIndex = nextIndex;
    };

    // 3. Overlay Toggle Helper
    window.toggleOverlay = function(id, show) {
        const overlay = document.getElementById(id);
        if (show) {
            overlay.classList.remove('opacity-0', 'invisible', 'pointer-events-none');
            overlay.classList.add('opacity-100', 'visible');
        } else {
            overlay.classList.remove('opacity-100', 'visible');
            overlay.classList.add('opacity-0', 'invisible', 'pointer-events-none');
        }
    };

    window.navigateToDashboard = function() {
        document.querySelectorAll('.slide').forEach(slide => {
            slide.classList.add('hidden');
        });
        const dashboard = document.getElementById('dashboard');
        dashboard.classList.remove('hidden');
    };

    window.returnToHome = function() {
        const dashboard = document.getElementById('dashboard-overlay');
        dashboard.classList.add('hidden');

        document.querySelectorAll('.slide').forEach(slide => {
            slide.classList.remove('hidden');
        });

        if (typeof window.updateSlides === 'function') {
            window.updateSlides(0);
        }
    };

    // 4. Attach Navigation Listeners
    document.getElementById('nav-home').addEventListener('click', () => updateSlides(0));
    document.getElementById('nav-faq').addEventListener('click', () => toggleOverlay('faq-overlay', true));
    document.getElementById('nav-dashboard').addEventListener('click', () => toggleOverlay('dashboard-overlay', true));
    document.getElementById('nav-team').addEventListener('click', () => toggleOverlay('team-overlay', true));
    document.getElementById('nav-about').addEventListener('click', () => toggleOverlay('about-overlay', true));

    // 5. Scroll Event
    document.getElementById('intro-container').addEventListener('wheel', (e) => {
        if (isScrollingLocked) return;
        if (e.deltaY > 30 && currentSlideIndex < slides.length - 1) {
            isScrollingLocked = true;
            updateSlides(currentSlideIndex + 1);
            setTimeout(() => isScrollingLocked = false, 1100);
        } else if (e.deltaY < -30 && currentSlideIndex > 0) {
            isScrollingLocked = true;
            updateSlides(currentSlideIndex - 1);
            setTimeout(() => isScrollingLocked = false, 1100);
        }
    }, { passive: true });

    // --- CAMERA, UPLOAD, AND GAME LOOP CONTROLS ---
    const video = document.getElementById('webcam-feed');
    const previewImage = document.getElementById('preview-image');
    const btnCapture = document.getElementById('btn-capture');
    const fileInput = document.getElementById('file-input');

    const placeholderIcon = document.getElementById('placeholder-icon');
    const placeholderText = document.getElementById('placeholder-text');

    const sectionCapture = document.getElementById('section-capture');
    const sectionQuiz = document.getElementById('section-quiz');
    const sectionRetry = document.getElementById('section-retry');

    const laser = document.getElementById('scanner-laser');
    const hintLabel = document.getElementById('detected-material-hint');
    const scoreDisplay = document.getElementById('user-score');

    let localStream = null;
    let currentCorrectAnswer = "";
    let currentScore = 0;

    // --- Helper: Reset UI States ---
    function clearPreviewContainer() {
        placeholderIcon.classList.add('hidden');
        placeholderText.classList.add('hidden');
        video.classList.add('hidden');
        previewImage.classList.add('hidden');
    }

    // Dynamic Visibility Manager
    function activeSection(section) {
        sectionCapture.classList.add('hidden');
        sectionQuiz.classList.add('hidden');
        sectionRetry.classList.add('hidden');

        if (section === 'capture') sectionCapture.classList.remove('hidden');
        if (section === 'quiz') sectionQuiz.classList.remove('hidden');
        if (section === 'retry') sectionRetry.classList.remove('hidden');
    }

    // --- 1. UPLOAD LOGIC ---
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            stopCamera();

            const reader = new FileReader();
            reader.onload = (event) => {
                clearPreviewContainer();
                previewImage.src = event.target.result;
                previewImage.classList.remove('hidden');
                
                // CONNECTED: Send uploaded base64 data to backend
                uploadToFlaskBackend(event.target.result);
            };
            reader.readAsDataURL(file);
        }
    });

    // --- 2. CAPTURE LOGIC ---
    btnCapture.addEventListener('click', async () => {
        // State A: Camera is NOT running -> Turn it on
        if (!localStream) {
            try {
                localStream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' }, 
                    audio: false 
                });
                
                clearPreviewContainer();
                video.srcObject = localStream;
                video.classList.remove('hidden');
                
                btnCapture.textContent = "TAKE SNAPSHOT";
                btnCapture.classList.replace('bg-emerald-700', 'bg-red-700'); 
            } catch (err) {
                console.error("Camera access blocked or unavailable: ", err);
                alert("Unable to access camera device.");
            }
        } 
        // State B: Camera IS running -> Freeze frame and save picture
        else {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const base64Data = canvas.toDataURL('image/jpeg');
            
            clearPreviewContainer();
            previewImage.src = base64Data;
            previewImage.classList.remove('hidden');
            
            stopCamera();

            // CONNECTED: Send snapshot data to backend
            uploadToFlaskBackend(base64Data);
        }
    });

    // --- Helper: Turn off Camera Hardware ---
    function stopCamera() {
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            localStream = null;
            video.srcObject = null;
        }
        btnCapture.textContent = "CAPTURE";
        btnCapture.classList.replace('bg-red-700', 'bg-emerald-700');
    }

    // Function triggered right after an image file is selected or snapshot is taken
    async function uploadToFlaskBackend(base64Image) {
        laser.classList.remove('hidden'); // Turn on laser animation
        
        try {
            // CONNECTED: Pointing to updated DB-connected backend route
            const response = await fetch('http://localhost:5000/api/classify', {
    method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    image: base64Image,
                    username: "Guest" // Adjust dynamic username variable here as needed
                })
            });
            
            const data = await response.json();
            laser.classList.add('hidden'); // Stop animation
            
            if (!data.valid) {
                alert("⚠️ SYSTEM FAILURE: UNIDENTIFIED OBJECT.");
                resetDashboard();
                return;
            }

            // Set up Quiz values received from Flask App
            currentCorrectAnswer = data.category;
            hintLabel.textContent = data.material; 
            
            activeSection('quiz'); 
            
        } catch (err) {
            console.error("Backend transmission error:", err);
            laser.classList.add('hidden');
        }
    }

    // Handle Quiz selection mechanics
    document.querySelectorAll('.btn-choice').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const choice = e.target.getAttribute('data-choice');
            
            if (choice === currentCorrectAnswer) {
                // Persistent Reward Call to Backend DB
                try {
                    await fetch('http://localhost:5000/api/classify', {
    method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: "Guest", // Pass variable matching your state setup
                            material: hintLabel.textContent,
                            points: 10
                        })
                    });
                    
                    currentScore += 10;
                    scoreDisplay.textContent = currentScore;
                    alert("🎯 CORRECT PROFILE SELECTED! +10 PTS");
                } catch(err) {
                    console.error("Error updating user stats:", err);
                }
                
                resetDashboard();
            } else {
                activeSection('retry'); 
            }
        });
    });

    // Retry Event Listeners
    document.getElementById('btn-try-again').addEventListener('click', () => activeSection('quiz'));
    document.getElementById('btn-reset-dash').addEventListener('click', resetDashboard);

    function resetDashboard() {
        activeSection('capture');
        document.getElementById('preview-image').classList.add('hidden');
        document.getElementById('placeholder-icon').classList.remove('hidden');
        document.getElementById('placeholder-text').classList.remove('hidden');
    }
});