# Pet Match

Pet Match is a web application that allows users to create accounts, verify their email addresses, and interact with a pet-matching platform. The backend is built with **Flask** and **PostgreSQL**, and email verification is handled via **Flask-Mail** note that the email verification has been temporarily removed.

---

## Features

- User account creation with password hashing
- Logging in to existing accounts
- Database-driven backend using PostgreSQL

---

## Getting Started

These instructions will help you set up the project locally.

### Prerequisites

- Python 3.11+
- PostgreSQL
- pip for instalation of additional required fields
- GIT for downloading
- javascript version v20.18.0 or newer
- jest 30.1.0

### Installing

1. **Clone the repository:**

```bash
git clone https://github.com/Uhlric-W/pet_match.git
cd pet_match
```
2. **Database Setup**
Setup a postgreSQL database named "pet_app". Then run 
```bash
psql -d pet_app -f db/schema.sql
```

### Running

1. **Running the server:**
From the root folder (pet_match/) run
```bash
python -m backend.app
```

2. **Running frontend code**
In a webrowser open the following link http://127.0.0.1:5000/create_account.html to go to a scpecific page replace create_account.html with <filename>.html
