# User Profile Feature Documentation

## Overview
The AI Coach application now includes a comprehensive user profile system with authentication, progress tracking, dashboard, and personalized recommendations.

## Features Implemented

### 1. User Authentication
- **Login System**: Simple username/password authentication
- **Default Users** (for development):
  - Username: `admin` | Password: `admin123`
  - Username: `user1` | Password: `password123`
- **Session Management**: User session maintained across Streamlit pages

### 2. User Profile Page
- **Dashboard**: Key metrics including:
  - Total training sessions
  - Total assessments completed
  - Total mentor queries
  - Total training time
- **Learning Progress**:
  - Completed levels by knowledge base
  - Knowledge bases explored
  - Levels attempted
- **Account Information**:
  - Username and email
  - Member since date
  - Last activity timestamp

### 3. Progress Tracking
- **Automatic Tracking**: Progress is automatically saved when:
  - User completes a training session
  - User submits an assessment
  - User asks a mentor question
- **Data Storage**: User progress stored in `data/user_progress.json`

### 4. Personalized Recommendations
- **Smart Recommendations**: AI Coach provides personalized learning suggestions based on:
  - Training history
  - Level progression
  - Knowledge base coverage
  - Assessment completion
  - Mentor usage
- **Priority Levels**: Recommendations prioritized as High, Medium, or Low

## Backend API Endpoints

### Authentication
- `POST /auth/login` - Authenticate user with username/password
  - Request: `{"username": "admin", "password": "admin123"}`
  - Response: `{"success": true, "user": {...}}`

### User Profile
- `GET /user/{username}/profile` - Get user profile information
- `GET /user/{username}/progress` - Get user's learning progress
- `GET /user/{username}/statistics` - Get user statistics for dashboard
- `GET /user/{username}/recommendations` - Get personalized recommendations
- `POST /user/progress/update` - Update user's learning progress

## Frontend Pages

### Login Page (`pages/0_login.py`)
- Login form with username and password
- Shows demo credentials
- Session state management
- Logout functionality

### Profile Page (`pages/4_profile.py`)
- Comprehensive dashboard with metrics
- Learning progress visualization
- Personalized recommendations
- Account information display
- Logout button

### Updated Pages
- **Training Page**: Tracks progress after successful training
- **Assessment Page**: Tracks progress after assessment submission
- **Mentor Page**: Tracks mentor queries
- **Home Page**: Shows login status

## Data Storage

### User Data (`data/users.json`)
Stores user authentication information:
```json
{
  "admin": {
    "username": "admin",
    "password": "admin123",
    "email": "admin@example.com",
    "created_at": "2024-12-31T..."
  }
}
```

### Progress Data (`data/user_progress.json`)
Stores user learning progress:
```json
{
  "admin": {
    "username": "admin",
    "training_sessions": [...],
    "assessments": [...],
    "mentor_queries": [...],
    "completed_levels": {...},
    "total_training_time": 0,
    "last_activity": "..."
  }
}
```

## Usage Instructions

### 1. Start Backend
```bash
./run_backend.sh
```

### 2. Start Frontend
```bash
./run_frontend.sh
```

### 3. Login
1. Navigate to the **Login** page (first in sidebar)
2. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
3. Click "Login"

### 4. View Profile
1. Navigate to **Profile** page from sidebar
2. View dashboard, progress, and recommendations

### 5. Track Progress
- Complete training sessions → Progress automatically saved
- Submit assessments → Progress automatically saved
- Ask mentor questions → Progress automatically saved

## Future Enhancements

### Potential Additions:
1. **User Registration**: Allow new users to create accounts
2. **Password Hashing**: Secure password storage (currently plain text for demo)
3. **Database Integration**: Replace JSON files with proper database
4. **Advanced Analytics**: More detailed learning analytics
5. **Achievement System**: Badges and achievements for milestones
6. **Learning Paths**: Structured learning paths based on progress
7. **Social Features**: Share progress, leaderboards
8. **Export Progress**: Download progress reports

## Security Notes

⚠️ **Current Implementation is for Development Only**:
- Passwords stored in plain text
- No password hashing
- No session tokens (using Streamlit session state)
- No rate limiting
- No input validation beyond basic checks

For production, implement:
- Password hashing (bcrypt, argon2)
- JWT tokens for authentication
- Database with proper security
- Input validation and sanitization
- Rate limiting
- HTTPS only

## File Structure

```
services/
  ├── user_service.py          # User authentication and progress tracking logic
  └── main.py                  # Updated with user endpoints

pages/
  ├── 0_login.py              # Login page (appears first)
  ├── 1_training.py           # Updated with progress tracking
  ├── 2_mentor.py             # Updated with progress tracking
  ├── 3_assessment.py         # Updated with progress tracking
  └── 4_profile.py            # Profile dashboard page

data/
  ├── users.json              # User authentication data
  └── user_progress.json      # User learning progress
```

## Testing

To test the feature:
1. Login with `admin` / `admin123`
2. Complete a training session
3. Check profile page - should show 1 training session
4. Submit an assessment
5. Check profile page - should show 1 assessment
6. View recommendations - should suggest next steps

## Troubleshooting

### Backend not responding
- Ensure backend is running: `./run_backend.sh`
- Check backend logs for errors

### Login fails
- Verify username/password are correct
- Check backend is running and accessible
- Check `data/users.json` exists and has default users

### Progress not saving
- Check user is logged in (session state)
- Verify backend endpoint is accessible
- Check `data/` directory is writable

### Profile page shows no data
- Complete some training/assessments first
- Check `data/user_progress.json` is being created
- Verify backend endpoints are working

