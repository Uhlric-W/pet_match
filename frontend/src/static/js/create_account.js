export async function send_new_account_info(account_info) {
    const response = await fetch("/create_account", {
        method: "POST",
        headers: { "Content-Type": "application/json"},
        body: JSON.stringify(account_info),
    });
    return response.json();
}

export function setup_create_account_form() {
    const form = document.getElementById("signupForm");
    const message = document.getElementById("signupMessage");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const confirm_password = document.getElementById("confirm_password").value;
        if ( password !== confirm_password ) { 
            message.textContent = "Passwords do not match";
            message.classList.remove("success");
            message.classList.add("error");
            return;
        }
        try {
            const result = await send_new_account_info({
                username,
                email,
                password,
                confirm_password,
            });
            if (result.error) {
                message.textContent = result.error;
                message.classList.remove("success");
                message.classList.add("error");
            } else {
                message.textContent = result.message || "Account created successfully";
                message.classList.remove("error");
                message.classList.add("success");
            }
        } catch (err) {
            message.textContent = "Server error, please try again later";
            message.classList.remove("success");
            message.classList.add("error");
        }
    });
}

if (typeof window !== undefined) {
    window.addEventListener("DOMContentLoaded", setup_create_account_form);
}