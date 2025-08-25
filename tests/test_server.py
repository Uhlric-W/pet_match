import json
import requests
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
    cur.close()


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
            for table in TABLES_TO_RESET:
                reset_table(table)
            print("Tables have been cleared")
    def setUp(cls):
        cls.test_user = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "MySecurePassword123"
        }
        cls.verification_token = None
        cls.login_user = {
            "username": "loginUser",
            "email": "loginUser@gmail.com",
            "password": "MySecurePassword123"
        }
        cls.test_user1 = {
            "username": "",
            "email": "testuser@gmail.com",
            "password": "MySecurePassword123"
        }
        cls.test_user2 = {
            "username": "testuser2",
            "email": "testuser@gmail.com",
            "password": ""
        }
        cls.test_user3 = {
            "username": "testuser3",
            "email": "",
            "password": "MySecurePassword123"
        }
        cls.test_user4a = {
            "username": "testuser4",
            "email": "othertestuser@gmail.com",
            "password": "MySecurePassword123" 
        }
        cls.test_user4b = {
            "username": "testuser4",
            "email": "uhlricgamer@gmail.com",
            "password": "MySecurePassword123"
        }
        cls.test_user4c = {
            "username": "testuser4c",
            "email": "othertestuser@gmail.com",
            "password": "MySecurePassword"
        }
        cls.login_test1 = {
            "username": "testuser",
            "password": "MySecurePassword123"
        }
        cls.login_test2 = {
            "username": "notauser",
            "password": "MySecurePassword123"
        }
        cls.login_test3 = {
            "username": "testuser",
            "password": "not_a_password"
        }
        cls.login_test4 = {
            "username": "",
            "password": "MySecurePassword123"
        }
        cls.login_test5 = {
            "username": "testuser",
            "password": ""
        }
        cls.login_test6 = {
            "username": "",
            "password": ""
        }
        cls.login_test7 = {
            "username": "wrong_user",
            "password": "wrong_password"
        }
    
    def test_1_create_account(self):

        response = requests.post(f"{BASE_URL}/create_account", json=self.test_user)
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
        response = requests.get(f"{BASE_URL}/verify_email/{ServerTests.verification_token}")
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
        response = requests.post(f"{BASE_URL}/create_account", json=self.test_user1)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty username")
    
    def test_4_empty_email(self):
        response = requests.post(f"{BASE_URL}/create_account", json=self.test_user2)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty email")

    def test_5_empty_password(self):
        response = requests.post(f"{BASE_URL}/create_account", json=self.test_user3)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty password")

    def test_6_duplicate_username(self):
        response = requests.post(f"{BASE_URL}/create_account", json=self.test_user4a)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        print("first user created:", data)
        response1 = requests.post(f"{BASE_URL}/create_account", json=self.test_user4b)
        self.assertEqual(response1.status_code, 409)
        data1 = response1.json()
        self.assertIn('error', data1)
        print("caught duplicate username")

    def test_7_duplicate_username(self):
        response1 = requests.post(f"{BASE_URL}/create_account", json=self.test_user4c)
        self.assertEqual(response1.status_code, 409)
        data1 = response1.json()
        self.assertIn('error', data1)
        print("caught duplicate email")
    
    def test_8_double_dup(self):
        response = requests.post(f"{BASE_URL}/create_account", json=self.test_user4a)
        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertIn('error', data)
        print("Caught double duplicate")

    def test_9_correct_login(self):
        response = requests.post(f"{BASE_URL}/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = requests.post(f"{BASE_URL}/login", json=self.login_test1)
        print(response)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("user_id", data)
        self.assertIn("message", data)
        print("login response:", data)

    def test_10_incorrect_username(self):
        response = requests.post(f"{BASE_URL}/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = requests.post(f"{BASE_URL}/login", json=self.login_test2)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
        print("Caught incorrect username")
    
    def test_11_incorrect_password(self):
        response = requests.post(f"{BASE_URL}/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = requests.post(f"{BASE_URL}/login", json=self.login_test3)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
        print("Caught incorrect password")
    
    def test_12_missing_username(self):
        response = requests.post(f"{BASE_URL}/create_account",json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = requests.post(f"{BASE_URL}/login", json=self.login_test4)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty username, login")
    
    def test_13_missing_password(self):
        response = requests.post(f"{BASE_URL}/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = requests.post(f"{BASE_URL}/login", json=self.login_test5)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught empty password, login")
    
    def test_14_missing_both(self):
        response = requests.post(f"{BASE_URL}/create_account",json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = requests.post(f"{BASE_URL}/login", json=self.login_test6)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        print("Caught double empty login")
    
    def test_15_double_incorrect(self):
        response = requests.post(f"{BASE_URL}/create_account", json=self.login_user)
        if response.status_code != 201 and response.status_code != 409:
            self.skipTest(f"Test skipped due to failure of account creation")
        response = requests.post(f"{BASE_URL}/login", json=self.login_test7)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
        print("Caught double incorrect fields")

if __name__ == "__main__":
    unittest.main()