import json
from backend.app import app
import unittest
import psycopg2
import os
import time
import webbrowser

BASE_URL = "http://localhost:5000"

DB_CONFIG = {
    'dbname': 'pet_app',
    'user': 'postgres',
    'password': 'P!zza102',
    'host': 'localhost',
    'port': 5432
}

TABLES_TO_RESET = ['users']

def reset_table(table_name):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
    conn.commit()
    cur.close()
    conn.close()


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client()
        with self.app.app_context():
            pass
    def tearDown(self):
        pass
    @classmethod
    def setUpClass(cls):
            cls.client = app.test_client()
            for table in TABLES_TO_RESET:
                reset_table(table)
            print("Tables have been cleared")
    def setUp(self):
        self.test_user = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.verification_token = None
        self.login_user = {
            "username": "loginUser",
            "email": "loginUser@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.test_user1 = {
            "username": "",
            "email": "testuser@gmail.com",
            "password": "MySecurePassword123"
        }
        self.test_user2 = {
            "username": "testuser2",
            "email": "testuser@gmail.com",
            "password": "",
            "confirm_password": ""
        }
        self.test_user3 = {
            "username": "testuser3",
            "email": "",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.test_user4a = {
            "username": "testuser4",
            "email": "othertestuser@gmail.com",
            "password": "MySecurePassword123" 
        }
        self.test_user4b = {
            "username": "testuser4",
            "email": "uhlricgamer@gmail.com",
            "password": "MySecurePassword123",
            "confirm_password": "MySecurePassword123"
        }
        self.test_user4c = {
            "username": "testuser4c",
            "email": "othertestuser@gmail.com",
            "password": "MySecurePassword",
            "confirm_password": "MySecurePassword"
        }
        self.login_test1 = {
            "username_or_email": "testuser",
            "password": "MySecurePassword123"
        }
        self.login_test2 = {
            "username_or_email": "notauser",
            "password": "MySecurePassword123"
        }
        self.login_test3 = {
            "username_or_email": "testuser",
            "password": "not_a_password"
        }
        self.login_test4 = {
            "username_or_email": "",
            "password": "MySecurePassword123"
        }
        self.login_test5 = {
            "username_or_email": "testuser",
            "password": ""
        }
        self.login_test6 = {
            "username_or_email": "",
            "password": ""
        }
        self.login_test7 = {
            "username_or_email": "wrong_user",
            "password": "wrong_password"
        }
        self.login_test8 = {
            "username_or_email": "loginuser@gmail.com",
            "password": "MySecurePassword123"
        }
    
    def test_1_create_account(self):

        response = self.client.post("/api/auth/create_account", json=self.test_user)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("user_id", data)
        self.assertIn("message", data)
        #user_id = data["user_id"]
        print("Create account response:", data)
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT verification_token FROM users WHERE email=%s", (self.test_user['email'],))
        token = cur.fetchone()
        #cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        #cur.execute("ALTER SEQUENCE users_id_seq RESTART WITH 1;")
        cur.close()
        conn.close()
        self.assertIsNotNone(token)
        ServerTests.verification_token = token[0]

    """def test_2_verify_email(self):
        print(self.verification_token)
        if not ServerTests.verification_token:
            self.skipTest("No verification token from previous test")
        response = self.client.get(f"/api/auth/verify_email/{ServerTests.verification_token}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        print("Verify email response:", data)
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT email_verified FROM users WHERE email=%s", (self.test_user['email'],))
        email_verified = cur.fetchone()[0]
        cur.close()
        conn.close()
        self.assertTrue(email_verified)"""

    def test_3_empty_username(self):
        response = self.client.post(f"/api/auth/create_account", json=self.test_user1)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty username")
    
    def test_4_empty_email(self):
        response = self.client.post(f"/api/auth/create_account", json=self.test_user2)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty email")

    def test_5_empty_password(self):
        response = self.client.post(f"/api/auth/create_account", json=self.test_user3)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty password")

    def test_6_duplicate_username(self):
        response = self.client.post(f"/api/auth/create_account", json=self.test_user4a)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        print("first user created:", data)
        response1 = self.client.post(f"/api/auth/create_account", json=self.test_user4b)
        self.assertEqual(response1.status_code, 409)
        data1 = response1.json()
        self.assertIn('error', data1)
        print("caught duplicate username")

    def test_7_duplicate_username(self):
        response1 = self.client.post(f"/api/auth/create_account", json=self.test_user4c)
        self.assertEqual(response1.status_code, 409)
        data1 = response1.json()
        self.assertIn('error', data1)
        print("caught duplicate email")
    
    def test_8_double_dup(self):
        response = self.client.post(f"/api/auth/create_account", json=self.test_user4a)
        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertIn('error', data)
        print("Caught double duplicate")

    def test_9_correct_login(self):
        response = self.client.post(f"/api/auth/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.login_test1)
        print(response)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("user_id", data)
        self.assertIn("message", data)
        print("login response:", data)

    def test_10_incorrect_username(self):
        response = self.client.post(f"/api/auth/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.login_test2)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
        print("Caught incorrect username")
    
    def test_11_incorrect_password(self):
        response = self.client.post(f"/api/auth/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.login_test3)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
        print("Caught incorrect password")
    
    def test_12_missing_username(self):
        response = self.client.post(f"/api/auth/create_account",json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.login_test4)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty username, login")
    
    def test_13_missing_password(self):
        response = self.client.post(f"/api/auth/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.login_test5)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty password, login")
    
    def test_14_missing_both(self):
        response = self.client.post(f"/api/auth/create_account",json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.login_test6)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught double empty login")
    
    def test_15_double_incorrect(self):
        response = self.client.post(f"/api/auth/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.login_test7)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
        print("Caught double incorrect fields")
    
    def test_16_login_email(self):
        response = self.client.post(f"/api/auth/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = self.client.post(f"/api/auth/login", json=self.login_test8)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("user_id", data)
        self.assertIn("message", data)
        print("login response", data)
        

if __name__ == "__main__":
    unittest.main()