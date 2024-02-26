# Flask OAuth JWT Web Application

This README outlines the setup, configuration, and features of the Flask web application designed to authenticate users via OAuth 2.0, issue JWT access tokens for authorization, and store KYC data and authentication/authorization activities in MongoDB. The application is containerized with Docker for ease of deployment and scalability.

## Table of Contents

1. [Introduction](#introduction)
2. [Technologies Used](#technologies-used)
3. [Getting Started](#getting-started)
   - [Installation](#installation)
   - [Configuration](#configuration)
4. [Application Features](#application-features)
5. [API Endpoints](#api-endpoints)
6. [Security Measures](#security-measures)
7. [Testing Flow](#testing-flow)
8. [Deployment](#deployment)
9. [Contributing](#contributing)
10. [License](#license)

## Introduction

This Flask web application allows users to authenticate using OAuth 2.0 with providers such as Google and GitHub. Upon successful authentication, users are issued JWT access tokens, enabling them to access protected routes within the application. The application records KYC data along with authentication and authorization activities in a MongoDB database, ensuring that user interactions are logged for security and auditing purposes.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python.
- **MongoDB**: A NoSQL database for storing user and activity data.
- **Docker**: A platform for developing, shipping, and running applications in containers.
- **OAuth 2.0**: An authorization framework that enables applications to obtain limited access to user accounts.
- **JWT (JSON Web Tokens)**: A compact, URL-safe means of representing claims to be transferred between two parties.

## Getting Started

### Installation

1. **Prerequisites**: Ensure you have Docker installed on your system.
2. **Clone the repository**: `git clone https://github.com/agiletom/trumo-flask-oauth-jwt.git`
3. **Build the Docker container**: `docker build -t flack-kyc-app .`
4. **Run the container**: `docker run --env-file .env -p 3000:3000 -d flack-kyc-app`

### Configuration

- Configure OAuth 2.0 providers by updating the `OAUTH2_PROVIDERS` in your application settings.
- Set environment variables for `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and MongoDB connection details (`DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`).

## Application Features

- OAuth 2.0 authentication with Google and GitHub.
- JWT access token issuance for authorization.
- KYC data and user activity logging in MongoDB.
- Containerization with Docker for easy deployment.

## API Endpoints

- `/`: Home page.
- `/authorize/<provider>`: Initiates OAuth 2.0 authorization with the specified provider.
- `/callback/<provider>`: Handles OAuth 2.0 callback from the provider.
- `/activities`: Fetches user activity logs. Requires JWT authentication.

## Security Measures

- Secure OAuth 2.0 implementation with state parameter to mitigate CSRF attacks.
- JWT tokens for secure, stateless authentication and authorization.
- Environment variables for sensitive configuration to avoid hard-coded credentials.

## Testing Flow

This section outlines the steps to test the application's functionality, specifically focusing on signing in using Single Sign-On (SSO) providers, obtaining JWT access tokens, and accessing user activity logs.

### Signing in with an SSO Provider

1. **Initiate Sign-In**: Navigate to the `/authorize/<provider>` endpoint in your web browser, replacing `<provider>` with either `google` or `github` to initiate authentication with the respective OAuth 2.0 provider.
2. **Complete Authentication**: Follow the prompts to log in with your chosen provider. Upon successful authentication, you will be redirected to a callback URL.

### Obtaining an Access Token

After successful sign-in, the application will issue a JWT access token. This token is displayed on the redirection page or returned in the application's response, depending on the implementation. Ensure to copy this token for the next steps.

### Accessing Activity Logs with Postman

1. **Open Postman**: Launch the Postman application or use its web version.
2. **Configure the Request**:
   - Set the request type to `GET`.
   - Enter the URL for the activities endpoint: `http://localhost:3000/activities`.
3. **Set the JWT Token**:
   - Navigate to the "Authorization" tab in Postman.
   - Select "Bearer Token" as the type.
   - Paste the JWT access token you obtained earlier into the token field.
4. **Send the Request**: Click the "Send" button. If the token is valid, you will receive a response containing the user's activity logs.

### Interpreting the Response

The response from the `/activities` endpoint provides a detailed log of the user's authentication and authorization activities within the application. This information is useful for auditing and monitoring purposes.

## Deployment

The application is containerized using Docker, facilitating easy deployment to various environments. The `Dockerfile` included in the repository defines the container setup.