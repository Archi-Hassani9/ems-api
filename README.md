# Event Management System API

A Django REST Framework based backend that allows users to create events, RSVP, and submit reviews.  
The project includes JWT authentication, custom permissions, filtering/search, and role-based access for event organizers.

---

## Features

- User authentication using JWT
- Create, update, delete events (organizer only)
- RSVP to events with status (Going, Maybe, Not Going)
- Add and view event reviews
- Private event access for invited users only
- Search and filter events by title, location, and organizer
- Admin panel available for full control

---

## Tech Stack

| Category | Technology |
|---------------------|--------------------------------------|
| Backend Framework   | Django, Django REST Framework        |
| Authentication      | JWT (djangorestframework-simplejwt)  |
| Database            | SQLite (default)                     |
| Async Tasks         | Celery + Redis (email notifications) |
| API Testing         | Thunder Client (VS Code)             |
| Python Version      | 3.8+                                 |

---

## Project Setup (Windows)

1. Clone the Repository
2. Create Virtual Environment
python -m venv venv
3. Activate Virtual Environment (PowerShell)
venv\Scripts\Activate.ps1
4. Install Requirements
pip install -r requirements.txt
5. Apply Migrations
python manage.py migrate
6. Run the Server
python manage.py runserver

Server will run at
http://127.0.0.1:8000/


Admin Credentials
Admin Panel: http://127.0.0.1:8000/admin
Username: admin
Password: archi9events
Email: archihassani9@gmail.com


Authentication (JWT)
1. Get Token (Login)
POST /api/token/
Body (JSON)
{
  "username": "admin",
  "password": "archi9events"
}

Response contains:
access token
refresh token

Use the access token in all authorized requests:
Authorization: Bearer <token>


API Endpoints
Method	         Endpoint	                             Description	                                  Auth Required
POST	   /events/	                                    Create event	                                      Yes
GET	     /events/	                          List public events (search & filter enabled)	                No
GET	     /events/{id}/	                              Event details	                                  Yes for private
PUT	     /events/{id}/	                        Update event (organizer only)	                            Yes
DELETE	 /events/{id}/                        	Delete event (organizer only)                     	      Yes
POST	   /events/{event_id}/rsvp/	                    RSVP to event	                                      Yes
PATCH	   /events/{event_id}/rsvp/{user_id}/	          Update RSVP	                                        Yes
POST	   /events/{event_id}/reviews/	                Add review	                                        Yes
GET	     /events/{event_id}/reviews/	                View reviews	                                      No


Celery & Email Notifications:
Celery is included for sending async email updates.
Start workers using:
celery -A ems_api worker -l info
Redis must be running as the message broker.


Notes

Project uses SQLite by default; change DATABASES in settings.py if needed.
Thunder Client collection can be exported from VS Code if needed.
