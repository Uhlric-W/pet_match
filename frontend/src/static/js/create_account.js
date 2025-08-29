document.getElementById("signupForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirm_password = document.getElementById("confirm_password").value;
    const controller = new AbortController();
    const timeout = setTimeout(() => {
        controller.abort();
        alert("Server failed to respond, try again later");
        window.location.reload();
    }, 5000);
    // sends the submitted information to the server
    try {
        const response = await fetch("/create_account", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                email,
                password,
                confirm_password
            })
        });

        const result = await response.json();
        const signup_message = document.getElementById("signupMessage");

        if (response.ok) {
            signup_message.style.color = "green";
            signup_message.textContent = result.message; 

            setTimeout(() => {
                window.location.href("/login.html");
            }, 1500);
        } else {
            signup_message.style.color = "red";
            signup_message.textContent = result.error || `Error ${response.status}`;
        }

    } catch (err) {
        console.error(err);
        document.getElementById("signupMessage").textContent = "Network or server error.";
    }
});