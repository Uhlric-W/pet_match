/**
 * @jest-environment jsdom
 */
import { setup_create_account_form, send_new_account_info } from "../src/static/js/create_account.js";

global.fetch = jest.fn();
const waitForNextTick = () => new Promise(process.nextTick);
describe("Create Account Form", () => {
    const main_parameters = {
        username: "testuser",
        email: "testuser@gmail.com",
        password: "MySecurePassword123",
        confirm_password: "MySecurePassword123"
    };
    beforeEach(() => {
        fetch.mockClear();
    });
    test("send_new_account_info calls fetch with correct payload", async () => {
        fetch.mockResolvedValueOnce({
            json: () => Promise.resolve({ message: "Account created successfully" }),
        });
        const result = await send_new_account_info(main_parameters);
        expect(fetch).toHaveBeenCalledWith(
            "/create_account",
            expect.objectContaining({
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(main_parameters),
            })
        );
        expect(result).toEqual({ message: "Account created successfully" });
    });

    test("returns success response from server", async () => {
        const mock_success_response = { message: "Account created successfully" };
        fetch.mockResolvedValueOnce({
            json: () => Promise.resolve(mock_success_response),
        });
        const result = await send_new_account_info(main_parameters);
        expect(result).toEqual(mock_success_response);
    });

    test("returns error response from server", async() => {
        const mock_error_response = { error: "Username already exists" };
        fetch.mockResolvedValueOnce({
            json: () => Promise.resolve(mock_error_response),
        });
        const result = await send_new_account_info(main_parameters);
        expect(result).toEqual(mock_error_response);
    });

    test("handles unexpected server response type", async () => {
        const mock_weird_response = { weird_type: "weird message" };
        fetch.mockResolvedValueOnce({
            json: () => Promise.resolve(mock_weird_response),
        });
        const result = await send_new_account_info(main_parameters);
        expect(result).toEqual(mock_weird_response);
    });

    test("throw if network error", async() => {
        fetch.mockRejectedValueOnce(new Error("Network error"));
        await expect(send_new_account_info(main_parameters)).rejects.toThrow("Network error");
    });

    test("setup_create_account_form shows success message on valid form submit", async () => {
        document.body.innerHTML = `
            <form id="signupForm">
                <input type="text" id="username" value="testuser">
                <input type="email" id="email" value="testuser@gmail.com">
                <input type="password" id="password" value="MySecurePassword123">
                <input type="password" id="confirm_password" value="MySecurePassword123">
                <button type="submit">Create Account</button>
            </form>
            <p id="signupMessage"></p>
        `;
        setup_create_account_form();
        fetch.mockResolvedValueOnce({
            json: () => Promise.resolve({ message: "Account created successfully" }),
        });
        const form = document.getElementById("signupForm");
        form.dispatchEvent(new Event("submit"));
        await waitForNextTick();
        const message = document.getElementById("signupMessage");
        expect(message.textContent).toBe("Account created successfully");
        expect(message.classList.contains("success")).toBe(true);
        expect(message.classList.contains("error")).toBe(false);
    });

    test("setup_create_account_form shows error when passwords don't match", async () => {
        document.body.innerHTML = `
            <form id="signupForm">
                <input type="text" id="username" value="testuser">
                <input type="email" id="email" value="testuser@gmail.com">
                <input type="password" id="password" value="MySecurePassword123">
                <input type="password" id="confirm_password" value="wrongPassword">
                <button type="submit">Create Account</button>
            </form>
            <p id="signupMessage"></p>
        `;
        setup_create_account_form();
        const form = document.getElementById("signupForm");
        form.dispatchEvent(new Event("submit"));
        await waitForNextTick();
        const message = document.getElementById("signupMessage");
        expect(message.textContent).toBe("Passwords do not match");
        expect(message.classList.contains("error")).toBe(true);
        expect(message.classList.contains("success")).toBe(false);
    });

});