# Water Quality Measuring System - Backend

This repository contains the backend code for the Water Quality Measuring System. The backend is built using Django and handles data storage, user authentication, real-time data transmission, and provides APIs for the frontend.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- **API:** Provides endpoints for data retrieval and user authentication.
- **Admin Dashboard:** Admin interface for managing the system and viewing detailed data.
- **Database:** Stores water quality data and user information.
- **Real-Time Data:** Uses Django Channels for real-time data transmission.
- **User Data:** Provides users with their own data through the API.

## Technologies Used

- **Django:** Python-based web framework.
- **Django Channels:** Adds real-time capabilities to Django applications.
- **PostgreSQL:** Database for storing water quality data.
- **Redis:** In-memory data structure store used for caching and as a channel layer for Django Channels.
- **uWSGI:** Application server for serving Django applications.
- **Nginx:** Web server and reverse proxy.

## Setup and Installation

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/davideke1/IIITH-backend.git
    cd IIITH-backend
    ```

2. Create a `.env.dev` file in the `backend` directory and add your environment variables:
    ```bash
    DJANGO_SECRET_KEY=your_secret_key
    POSTGRES_DB=#####
    POSTGRES_USER=####
    POSTGRES_PASSWORD=####
    ```

3. Build and run the Docker containers:
    ```bash
    docker-compose up --build
    ```

4. Apply database migrations:
    ```bash
    docker exec -it django_app python manage.py migrate
    ```

5. Create a superuser for accessing the admin interface:
    ```bash
    docker exec -it django_app python manage.py createsuperuser
    ```

## Usage

1. Access the Django admin interface at `http://localhost/admin` for administrative tasks.
2. The backend APIs are accessible at `http://localhost/api/`.
3. Real-time data updates are handled through Django Channels.

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.
