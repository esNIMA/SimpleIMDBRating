
# API Documentation for Movie Critics Rating System

## Overview:
This API allows users to sign up, log in, rate movies, and provide feedback. Each movie is fetched from an external API (OMDb) if it doesn't exist in the database. Additionally, when a new critic is added for a movie, other users who have rated the same movie are notified via email.

## Endpoints:

---

### 1. User Authentication

#### POST users/signin/
**Description**: Registers a new user.

- **Request**:
    ```json
    {
        "username": "your_username",
        "password": "your_password",
        "password_confirm": "your_password",
        "email": "your_email@example.com"
    }
    ```

- **Response**:
    - **201 Created**: 
        ```json
        {
            "message": "User registered successfully"
        }
        ```
    - **400 Bad Request**: 
        ```json
        {
            "username": ["This username is already taken."]
        }
        ```

---

#### POST users/login/
**Description**: Authenticates a user and returns a token for future authenticated requests.

- **Request**:
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```

- **Response**:
    - **200 OK**:
        ```json
        {
            "token": "your_token",
            "user_id": 1,
            "email": "your_email@example.com"
        }
        ```
    - **401 Unauthorized**:
        ```json
        {
            "error": "Invalid credentials"
        }
        ```

---

### 2. Critics Management

#### POST /critics/critics/
**Description**: Allows users to submit or update a movie critic. If the user has already rated the movie, the new rating replaces the old one. Additionally, users who have previously rated the movie will be notified via email.

- **Authentication**: Required (via Token in the header).
- **Request**:
    ```json
    {
        "movie_name": "The Godfather",
        "criticText": "Amazing movie with excellent direction.",
        "criticRating": 5
    }
    ```

- **Response**:
    - **201 Created**:
        ```json
        {
            "message": "Critic added successfully"
        }
        ```
    - **400 Bad Request**:
        ```json
        {
            "movie_name": ["Movie not found in external API."]
        }
        ```

#### Internal Logic:
- The `CriticSerializer` is responsible for validating and saving critics. If the movie does not exist in the local database, it will fetch it from OMDb API.
- If the critic exists, the existing rating will be updated, otherwise, a new entry will be created.
- Once a critic is created, users who have previously written reviews for that movie will be notified via email.

---

### 3. Email Notification System
When a new critic is added for a movie, the API will notify all users who have previously written a critic for that movie, excluding the user who added the new critic.

- **Email Structure**:
    - **Subject**: "New Critic Added for [Movie Name]"
    - **Message**: "A new critic has been added for the movie '[Movie Name]' by '[Username]'. Check it out!"
    - The email is sent using Django’s `send_mail` method with recipients being the email addresses of users who have already reviewed the movie.

---

## Models

### 1. Movies Model
Represents movies stored in the database.
- **Fields**:
    - `movieId` (AutoField, Primary Key)
    - `movieName` (CharField, max_length=100)

### 2. Critics Model
Represents the reviews or ratings provided by users for movies.
- **Fields**:
    - `criticId` (AutoField, Primary Key)
    - `criticText` (TextField, max_length=500)
    - `criticRating` (IntegerField, default=1)
    - `user` (ForeignKey to the `User` model, on_delete=models.CASCADE)
    - `movieName` (ForeignKey to the `Movies` model, on_delete=models.CASCADE)

---

## External Dependencies:

### OMDb API:
- Movies are fetched using the OMDb API (`http://www.omdbapi.com/`). The movie name is passed as part of the query, and if the movie exists, it is added to the local database.

### Example of OMDb Request:
```python
api_key = 'your_api_key'
external_api_url = f'http://www.omdbapi.com/?apikey={api_key}&t={formatted_movie_name}'
response = requests.get(external_api_url)
```

### Email Configuration:
For sending emails, Django’s `send_mail` function is utilized. The email system needs to be configured with SMTP credentials in the `settings.py` file:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_password'
DEFAULT_FROM_EMAIL = 'your_email@gmail.com'
```

---

### Error Handling

- **500 Internal Server Error**: If there's an issue with the movie fetching or sending emails, a 500 error is raised.
