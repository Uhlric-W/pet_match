import unittest
from backend.app import app
import psycopg2

DB_CONFIG = {
    'dbname': 'pet_app',
    'user': 'postgres',
    'password': 'P!zza102',
    'host': 'localhost',
    'port': 5432
}
# summary: Reset tables between tests to ensure all tests run correctly
def reset_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    # the tables involved in the testing that should be reseted between iterations of the suite
    tables = ["users"]
    # restarts each of the tables
    for table in tables:
        cur.execute(f"TRUNCATE {table} RESTART IDENTITY CASCADE;")
    
    conn.commit()
    cur.close()
    conn.close()

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.testing = True
        cls.client = cls.app.test_client()
        reset_tables()
        print("All tables have been cleared for testing.")
    
    def setUp(self):
        self.create_account_user = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.ensure_login_works_user = {
            "username": "loginUser",
            "email": "loginUser@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.empty_username_user = {
            "username": "",
            "email": "testuser@gmail.com",
            "password": "MySecurePassword123"
        }
        self.empty_password_user = {
            "username": "testuser2",
            "email": "testuser@gmail.com",
            "password": "",
            "confirm_password": ""
        }
        self.empty_email_user = {
            "username": "testuser3",
            "email": "",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.base_duplicate_user = {
            "username": "testuser4",
            "email": "othertestuser@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.same_username_user = {
            "username": "testuser4",
            "email": "uhlricgamer@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.same_email_user = {
            "username": "testuser4c",
            "email": "othertestuser@gmail.com",
            "password": "MySecurePassword",
            "confirm_password": "MySecurePassword"
        }
        self.missing_confirm_user = {
            "username": "testuser5",
            "email": "anothertestuser@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": ""
        }
        self.mismatch_passwords_user = {
            "username": "testuser6",
            "email": "anothertestuser@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": "Mismatch123"
        }
        self.same_password_user = {
            "username": "newusername",
            "email": "thiswillwork@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.login_test_info = {
            "username_or_email": "testuser",
            "password": "MySecurePassword123"
        }
        self.nonexistant_user_login_test = {
            "username_or_email": "notauser",
            "password": "MySecurePassword123"
        }
        self.wrong_password_test = {
            "username_or_email": "testuser",
            "password": "not_a_password"
        }
        self.empty_username_login = {
            "username_or_email": "",
            "password": "MySecurePassword123"
        }
        self.empty_password_login = {
            "username_or_email": "testuser",
            "password": ""
        }
        self.empty_username_and_password_login = {
            "username_or_email": "",
            "password": ""
        }
        self.wrong_username_and_password = {
            "username_or_email": "wrong_user",
            "password": "wrong_password"
        }
        self.login_with_email = {
            "username_or_email": "loginUser@gmail.com",
            "password": "MySecurePassword123"
        }
        self.wrong_username_existing_password = {
            "username_or_email": "pumpernickle",
            "password": "MySecurePassword123"
        }

    def test_1_create_account(self):
        response = self.client.post("/api/auth/create_account", json = self.create_account_user)
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn("user_id", data)
        self.assertIn("message", data)
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT verification_token FROM users WHERE email = %s", (self.create_account_user['email'],))
        token = cur.fetchone()
        cur.close()
        conn.close()
        self.assertIsNotNone(token)
        print("Create account response:", data)

    def test_2_empty_username(self):
        response = self.client.post(f"/api/auth/create_account", json=self.empty_username_user)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught empty username")

    def test_3_empty_email(self):
        response = self.client.post(f"/api/auth/create_account", json=self.empty_password_user)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught empty email")

    def test_4_empty_password(self):
        response = self.client.post(f"/api/auth/create_account", json=self.empty_email_user)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught empty password")

    def test_5_duplicate_username(self):
        response = self.client.post(f"/api/auth/create_account", json=self.base_duplicate_user)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        print("first user created:", data)
        response1 = self.client.post(f"/api/auth/create_account", json=self.same_username_user)
        self.assertEqual(response1.status_code, 409)
        data1 = response1.get_json()
        self.assertIn('error', data1)
        print("caught duplicate username")

    def test_6_duplicate_email(self):
        response1 = self.client.post(f"/api/auth/create_account", json=self.same_email_user)
        self.assertEqual(response1.status_code, 409)
        data1 = response1.get_json()
        self.assertIn('error', data1)
        print("caught duplicate email")

    def test_7_double_dup(self):
        response = self.client.post(f"/api/auth/create_account", json=self.base_duplicate_user)
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught double duplicate")
    
    def test_8_correct_ensure_login_works_username(self):
        response = self.client.post(f"/api/auth/create_account", json=self.ensure_login_works_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.login_test_info)
        print(response)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("user_id", data)
        self.assertIn("message", data)
        print("login response:", data)
    
    def test_9_incorrect_username(self):
        response = self.client.post(f"/api/auth/create_account", json=self.ensure_login_works_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.nonexistant_user_login_test)
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught incorrect username")

    def test_10_incorrect_password(self):
        response = self.client.post(f"/api/auth/create_account", json=self.ensure_login_works_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.wrong_password_test)
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught incorrect password")

    def test_11_missing_username(self):
        response = self.client.post(f"/api/auth/create_account",json=self.ensure_login_works_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.empty_username_login)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught empty username, login")

    def test_12_missing_password(self):
        response = self.client.post(f"/api/auth/create_account", json=self.ensure_login_works_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.empty_password_login)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught empty password, login")

    def test_13_missing_both(self):
        response = self.client.post(f"/api/auth/create_account",json=self.ensure_login_works_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.empty_username_and_password_login)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught double empty login")

    def test_14_double_incorrect(self):
        response = self.client.post(f"/api/auth/create_account", json=self.ensure_login_works_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.wrong_username_and_password)
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)
        print("Caught double incorrect fields")
    
    def test_15_correct_login_email(self):
        response = self.client.post(f"/api/auth/create_account", json=self.ensure_login_works_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response1 = self.client.post(f"/api/auth/login", json=self.login_with_email)
        self.assertEqual(response1.status_code, 200)
        data = response1.get_json()
        self.assertIn("user_id", data)
        self.assertIn("message", data)
        print("login response", data)

    def test_16_missing_confirm(self):
        response = self.client.post(f"/api/auth/create_account", json=self.missing_confirm_user)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        print("caught missing confirm")
    
    def test_17_mismatch_passwords(self):
        response = self.client.post(f"/api/auth/create_account", json=self.mismatch_passwords_user)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        print("caught mismatch password confirmation field")

    def test_18_new_account_same_password(self):
        response = self.client.post(f"/api/auth/create_account", json=self.same_password_user)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("user_id", data)
        self.assertIn("message", data)
        print("Create Account Response: ", data)
    
    def test_19_not_an_account_password_of_other(self):
        response1 = self.client.post(f"/api/auth/create_account", json=self.ensure_login_works_user)
        response2 = self.client.post(f"/api/auth/login", json=self.wrong_username_existing_password)
        data2 = response2.get_json()
        if response1.status_code != 201 and response1.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        self.assertIn('error', data2)
        print("didn't login to account with matching password")