# Mergington High School Activities

A comprehensive web application that provides students and teachers with a full-featured platform for managing extracurricular activities at Mergington High School.

## Features

### Student Features
- **Browse Activities**: View all available extracurricular activities with detailed information
- **Advanced Filtering**: Filter activities by:
  - Category (Sports, Arts, Academic, Community, Technology)
  - Day of the week (Monday through Sunday)
  - Time of day (Before School, After School, Weekend)
- **Search Functionality**: Search activities by name or description
- **Activity Details**: View comprehensive information including schedules, descriptions, and participant counts
- **Responsive Design**: Optimized interface for desktop and mobile devices

### Teacher Features
- **Secure Authentication**: Role-based login system for teachers and administrators
- **Student Registration Management**: Register and unregister students for activities
- **Session Management**: Persistent login sessions with automatic validation
- **Activity Administration**: Full control over student enrollments

### Technical Features
- **RESTful API**: Comprehensive FastAPI backend with interactive documentation
- **Database Integration**: MongoDB for persistent data storage
- **Real-time Updates**: Dynamic content loading with skeleton screens
- **Security**: Argon2 password hashing and session validation

## Technical Stack

- **Backend**: FastAPI (Python web framework)
- **Database**: MongoDB with PyMongo driver
- **Frontend**: Vanilla JavaScript with modern ES6+ features
- **Authentication**: Argon2 password hashing
- **Server**: Uvicorn ASGI server
- **Styling**: Modern CSS with responsive design

## API Endpoints

### Activities
- `GET /activities` - Retrieve all activities (supports filtering by day, start_time, end_time)
- `GET /activities/days` - Get list of all days with scheduled activities
- `POST /activities/{activity_name}/signup` - Register a student for an activity (requires teacher authentication)
- `POST /activities/{activity_name}/unregister` - Remove a student from an activity (requires teacher authentication)

### Authentication
- `POST /auth/login` - Teacher login
- `GET /auth/check-session` - Validate user session

## Pre-configured Activities

The system comes with 12 diverse activities across multiple categories:
- **Sports**: Soccer Team, Basketball Team, Morning Fitness
- **Academic**: Math Club, Programming Class, Science Olympiad
- **Arts**: Art Club, Drama Club
- **Strategy**: Chess Club, Sunday Chess Tournament
- **Technology**: Weekend Robotics Workshop
- **Communication**: Debate Team

Each activity includes detailed scheduling, capacity limits, and participant management.

## Development Guide

For detailed setup and development instructions, please refer to our [Development Guide](../docs/how-to-develop.md).
