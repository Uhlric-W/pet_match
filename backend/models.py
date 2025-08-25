# class for user to temporarily store data between calls that matches the format of the database
class User:
    def __init__(self, id, username, email, password_hash, email_verified):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.email_verified = email_verified