document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('register-password');
    const toggleBtn = document.getElementById('toggle-password-btn');

    // 1. PASSWORD TOGGLE
    toggleBtn?.addEventListener('click', () => {
        const isPassword = passwordInput.type === 'password';
        passwordInput.type = isPassword ? 'text' : 'password';
        toggleBtn.textContent = isPassword ? '🙈' : '👁️';
    });

    // 2. AVATAR PREVIEW
    document.querySelectorAll('input[name="avatar"]').forEach(input => {
        input.addEventListener('change', (e) => {
            document.getElementById('avatar-preview').src = `assets/avatars/${e.target.value}.webp`;
        });
    });

    // 3. GUEST LOGIN
    document.getElementById("auth-login-btn")?.addEventListener("click", () => {
        localStorage.setItem("verte_user_profile", JSON.stringify({ username: "Guest_" + Math.floor(Math.random() * 9999), avatar: "assets/avatars/avatar1.webp" }));
        window.location.href = "dashboard.html";
    });

    // 4. SIGN IN (REGISTER)
    document.getElementById('auth-guestLogin-btn')?.addEventListener('click', async () => {
        const username = document.getElementById('username').value;
        const password = document.getElementById('register-password').value;
        const avatar = document.querySelector('input[name="avatar"]:checked')?.value || 'avatar1';

        try {
            const response = await fetch("http://localhost:5000/api/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password, avatar })
            });
            
            const data = await response.json();
            if (response.ok) {
                localStorage.setItem("verte_user_profile", JSON.stringify({ username, avatar }));
                window.location.href = "dashboard.html";
            } else {
                alert(data.message);
            }
        } catch (err) {
            console.error("Connection Error:", err);
            alert("Could not connect to the server. Ensure app.py is running!");
        }
    });

    // 5. LOG IN (VERIFY)
    document.getElementById('auth-submit-btn')?.addEventListener('click', async () => {
        const username = document.getElementById('username').value;
        const password = document.getElementById('register-password').value;

        try {
            const response = await fetch("http://localhost:5000/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("verte_user_profile", JSON.stringify({ username, avatar: data.avatar }));
                window.location.href = "dashboard.html";
            } else {
                alert("Invalid credentials.");
            }
        } catch (err) {
            console.error("Login Error:", err);
            alert("Could not connect to the server.");
        }
    });
    
    //guest login
    document.getElementById('auth-guestLogin-btn').addEventListener('click', async () => {
    const response = await fetch("http://localhost:5000/api/guest-login", { method: "POST" });
    const data = await response.json();
    
    if (response.ok) {
        // Store the guest profile in localStorage
        localStorage.setItem("verte_user_profile", JSON.stringify({ 
            username: data.username, 
            isGuest: true 
        }));
        window.location.href = "dashboard.html";
    }
});

    // 6. GENERATORS
    document.getElementById("generate-username-btn")?.addEventListener("click", () => {
        const prefixes = ["Eco", "Green", "Terra", "Verte"];
        const suffixes = ["Warrior", "Scout", "Sentinel", "Guardian"];
        document.getElementById("username").value = `${prefixes[Math.floor(Math.random() * prefixes.length)]}${suffixes[Math.floor(Math.random() * suffixes.length)]}${Math.floor(Math.random() * 900)}`;
    });
});