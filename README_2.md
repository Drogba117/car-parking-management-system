# Car Parking Management System
# ID:230103135
A streamlined, real-time web application for managing multi-level parking reservations and tracking driver trip history.

---

## Problem Statement

Finding parking in multi-floor facilities is often inefficient and frustrating. Drivers waste time searching for available spots, while manual systems lead to inaccurate occupancy tracking and billing errors.

This system solves these issues by providing:
- Real-time parking visualization
- Instant reservations
- Automated billing and tracking

---

##  Features

- **Real-time Occupancy Map**  
  Interactive grid showing free, occupied, and reserved spots across Levels A, B, and C.

- **Instant Reservations**  
  Book parking spots with a single click and get immediate status updates.

- **Trip History & Analytics**  
  View detailed logs of parking sessions including duration, cost, and spot type.

- **User Authentication**  
  Secure login and registration using phone number and license plate.

- **Automated Billing**  
  Dynamic pricing based on parking duration and spot type.

---

## Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript  
- **Backend:** Python (FastAPI)  
- **Database:** SQLite (SQLAlchemy ORM)  
- **Authentication:** JWT (JSON Web Tokens)

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
