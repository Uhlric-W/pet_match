export async function send_login_info(account_info) {
    const response = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(account_info),
    });
    return response.json();
}

export function setup_login_account_form() {
    const form = document.getElementById("loginForm");
    const message = document.getElementById("loginMessage");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username_or_email = document.getElementById("emailOrUsername").value;
        const password = document.getElementById("password");
        try {
            const result = await send_login_info({
                username_or_email,
                password,
            });
            if (result.error) {
                message.textContent = result.error;
                message.classList.remove("success");
                message.classList.add("error");
            } else {
                message.textContent = result.message || "Logged in successfully";
                message.classList.remove("error");
                message.classList.add("success");
            }
        }
        catch (err) {
            message.textContent = "Server error, please try again later";
            message.classList.remove("success");
            message.classList.add("error");
        }
    });
}

if (typeof window !== undefined) {
    window.addEventListener("DOMContentLoaded", setup_login_account_form);
}