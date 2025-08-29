export async function handleSignup(username, email, password, confirm_password) {
    const controller = new AbortController();
    const timeout = setTimeout(() => {
        controller.abort();
        alert("Server failed to respond, try again later");
        window.location.reload();
    }, 5000);

    try {
        const response = await fetch("/create_account", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password, confirm_password }),
            signal: controller.signal
        });

        const result = await response.json();
        return { ok: response.ok, result };

    } catch (err) {
        console.error(err);
        return { ok: false, error: "Network or server error." };
    } finally {
        clearTimeout(timeout);
    }
}

if (typeof document !== "undefined") {
    const form = document.getElementById("signupForm");
    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();
            const username = document.getElementById("username").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const confirm_password = document.getElementById("confirm_password").value;

            const { ok, result, error } = await handleSignup(username, email, password, confirm_password);
            const signup_message = document.getElementById("signupMessage");

            if (ok) {
                signup_message.style.color = "green";
                signup_message.textContent = result.message;
                setTimeout(() => {
                    window.location.href = "/under_construction.html";
                }, 1500);
            } else {
                signup_message.style.color = "red";
                signup_message.textContent = error || result.error || "Signup failed.";
            }
        });
    }
}
