# API Reference

## Authentication Endpoints

### POST /api/auth/register
Register a new user.

### POST /api/auth/login
Login with email and password.

### POST /api/auth/refresh
Refresh JWT token.

### POST /api/auth/password-reset
Request password reset.

## Task Management Endpoints

### GET /api/tasks/
List all tasks for the authenticated user.

### POST /api/tasks/
Create a new task.

### GET /api/tasks/{id}/
Retrieve a specific task.

### PUT /api/tasks/{id}/
Update a specific task.

### DELETE /api/tasks/{id}/
Delete a specific task.

## AI Endpoints

### POST /api/ai/generate-schedule
Generate an optimized daily schedule.

### POST /api/ai/chat
Get AI assistance and motivation.

## Music Integration Endpoints

### GET /api/music/playlists
Get available playlists.

### POST /api/music/play
Start playing selected music.

## Analytics Endpoints

### GET /api/insights/
Get user insights and statistics.

### GET /api/insights/mood
Get mood tracking data.

More endpoints will be documented as they are implemented.