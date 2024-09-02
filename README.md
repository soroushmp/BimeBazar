# Project Name

## Overview

This project is a Django application with a pre-configured Docker environment. It includes built-in support for Swagger and Redoc documentation, as well as an Admin Dashboard. 

## Getting Started

Follow these steps to set up and run the application locally:

### Prerequisites

- Docker
- Docker Compose

### Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/soroushmp/BimeBazar.git
    cd BimeBazar
    ```

2. **Create Environment File**

    Copy the example environment file to create your own `.env` file:

    ```bash
    cp example-env.txt .env
    ```

    Update the `.env` file with your environment-specific settings if needed.

3. **Build and Run the Docker Containers**

    ```bash
    docker-compose up --build
    ```

    This command will build the Docker image and start the containers. It will also automatically install required packages and load fixture data.

### Accessing the Application

- **Swagger Documentation:** [http://127.0.0.1](http://127.0.0.1)
- **Redoc Documentation:** [http://127.0.0.1/redoc/](http://127.0.0.1/redoc/)
- **Admin Dashboard:** [http://127.0.0.1/admin](http://127.0.0.1/admin)

### Superuser Credentials

- **Username:** `root`
- **Password:** `root`

Use these credentials to access the Admin Dashboard.
