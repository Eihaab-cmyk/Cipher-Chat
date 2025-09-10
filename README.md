# Cipher-Chat

## Project Overview

The Cipher chat Project is a full-stack web application designed to facilitate real-time chat functionality. It includes a backend built with Node.js and Express, and a frontend developed using React. The application supports user authentication, group chats, and real-time messaging.

### Features

- User authentication (login and signup)
- Real-time messaging through socket.io
- Group chat creation and management
- User profile management
- Responsive design for seamless usage across devices

## Project Structure

### Backend

The backend is located in the `backend` folder and includes the following key components:

- **Routes**: Define API endpoints for users, chats, messages, and image handling.
- **Controllers**: Handle the business logic for chats, messages, and users.
- **Models**: Define the database schema for chats, messages, and users.
- **Middlewares**: Include authentication and error handling logic.
- **Config**: Contains database connection and token generation logic.

### Frontend

The frontend is located in the `frontend` folder and includes the following key components:

- **Pages**: Define the main pages such as Homepage and ChatPage.
- **Components**: Reusable UI components like ChatBox, SideDrawer, and ProfileModal.
- **Context**: Manages global state for the chat application.
- **Config**: Contains utility functions for chat-related logic.

## Prerequisites

- Node.js (v14 or higher)
- MongoDB (local or cloud instance)
- npm or yarn

## Installation and Setup

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the `backend` directory and add the following variables:
   ```env
   MONGO_URI=your_mongodb_connection_string
   JWT_SECRET=your_jwt_secret
   ```
4. Start the backend server:
   ```bash
   npm run dev
   ```
   The backend server will run on `http://localhost:5000` by default.

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the frontend development server:
   ```bash
   npm start
   ```
   The frontend server will run on `http://localhost:3000` by default.

## Running the Application

1. Ensure the backend server is running on `http://localhost:5000`.
2. Ensure the frontend server is running on `http://localhost:3000`.
3. Open your browser and navigate to `http://localhost:3000` to use the application.

## License

This project is licensed under the MIT License.
