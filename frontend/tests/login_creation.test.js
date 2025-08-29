import { loadHTML } from "./utils";

describe("Auth Pages", () => {
    describe("Create Account Page", () => {
        beforeAll(() => {
            loadHTML("create_account.html");
        });

        test("renders signup form fields", () => {
            expect(document.getElementById("username")).not.toBeNull();
            expect(document.getElementById("email")).not.toBeNull();
            expect(document.getElementById("password")).not.toBeNull();
            expect(document.getElementById("confirm_password")).not.toBeNull();
        });
    });
});
