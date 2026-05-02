# Park App: Smart Parking Management System

## 230103118, 230103249, 230103135, 230103302



Park App is a full-stack solution designed to modernize urban parking management. By combining a high-performance FastAPI backend with an intuitive HTML5/JS frontend, the application streamlines the process of finding, reserving, and paying for parking spots.







---



## Problem Statement

Traditional parking management is often manual and inefficient. Drivers face frustration searching for available spots—particularly specialized spaces like Electric Vehicle (EV) charging stations—while lot operators struggle to track occupancy and calculate accurate billing for varying durations.



**Park App solves this by:**

* **Real-Time Visibility:** Providing a digital map of spot availability filtered by floor.

* **Smart Reservations:** Preventing "spot-stealing" through a secure, JWT-backed reservation system.

* **Automated Billing:** Eliminating manual errors by calculating costs based on precise timestamps and specific spot rates.



---



## Tech Specs & Stack



### Backend (API)

* **Language:** Python 3.9+

* **Framework:** FastAPI (Asynchronous, high-performance)

* **Database:** SQLite with SQLAlchemy ORM for relational data management.

* **Security:** JWT (JSON Web Tokens) for stateless, secure user sessions.

* **Validation:** Pydantic for robust data integrity and error handling.



### Frontend

* **Languages:** HTML5, CSS3, and Vanilla JavaScript.

* **Deployment:** Vercel.

* **Features:** Dynamic DOM manipulation for real-time spot status updates and LocalStorage integration for persistent user login.



---








## How It Works



### 1. Discovery and Filtering

The frontend communicates with the `/api/spots` endpoint to visually render the parking lot. Users can filter by floor to find available Standard or EV spots instantly.



### 2. Secure Reservation

Once a user selects a "free" spot, the system:

* Validates the user's identity via JWT.

* Updates the spot status to "reserved" in the database.

* Stores a timestamped reservation record to track the start of the session.



### 3. Automated Checkout & History

When a user ends their session, the backend calculates the duration and the total cost (Rate × Minutes). The spot is then returned to "free" status, and the session is archived in the user's **Trip History** for future reference.



---



### Core API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| POST | /api/auth/register | Register a new user and license plate | No |
| POST | /api/auth/login | Authenticate and receive access token | No |
| GET | /api/spots | View all spots (Optional floor filter) | No |
| POST | /api/spots/{id}/reserve | Reserve a specific parking spot | Yes |
| DELETE | /api/reservations/mine | End session and generate final bill | Yes |
| GET | /api/history | View list of all past parking trips | Yes |


---


## Installation

```bash
# Clone the repository
git clone https://github.com/Drogba117/car-parking-management-system.git

# Navigate to project folder
cd car-parking-management-system

# Install dependencies
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib

# Initialize database
python -m app.seed

# Run backend server
uvicorn app.main:app --reload
