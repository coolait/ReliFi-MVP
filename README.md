# ReliFi MVP

A gig work scheduling platform that helps users find and book optimal shifts across multiple platforms like Uber, Lyft, DoorDash, and more.

## Features

- **Weekly Calendar View**: Interactive calendar showing hourly time slots (6 AM - 11 PM)
- **Smart Recommendations**: Get top 3 gig opportunities for any selected time slot
- **Real-time Booking**: Add recommended shifts to your schedule with one click
- **Earnings Projections**: See projected earnings for each opportunity
- **Multi-platform Support**: Uber, Lyft, DoorDash, GrubHub, Uber Eats

## Quick Start

1. **Install Dependencies**:
   ```bash
   npm run install-all
   ```

2. **Start the Application**:
   ```bash
   npm start
   ```

   This will start both the backend server (port 5001) and frontend client (port 3000).

3. **Open in Browser**:
   Navigate to `http://localhost:3000` to view the application.

## Manual Setup

If you prefer to run the services separately:

### Backend Server
```bash
cd server
npm install
npm start
```

### Frontend Client
```bash
cd client
npm install
npm start
```

## Usage

1. **Select a Time Slot**: Click on any hourly slot in the weekly calendar
2. **View Recommendations**: The right panel will show the top 3 gig opportunities for that time
3. **Book a Shift**: Click "Add to My Schedule" to book any recommended opportunity
4. **Navigate Weeks**: Use the arrow buttons to navigate between different weeks

## Technology Stack

- **Frontend**: React + TypeScript + TailwindCSS
- **Backend**: Node.js + Express
- **API**: RESTful API with mock data
- **State Management**: React Hooks

## Project Structure

```
ReliFi-MVP/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.tsx        # Main app component
│   │   └── index.css      # TailwindCSS styles
│   └── package.json
├── server/                # Express backend
│   ├── index.js          # Server entry point
│   └── package.json
└── package.json          # Root package.json with scripts
```

## API Endpoints

- `GET /api/recommendations/:day/:hour` - Get gig recommendations for a specific time slot
- `GET /api/health` - Health check endpoint

## Mock Data

The application currently uses mock data for demonstration purposes. The backend includes sample gig opportunities with realistic earnings projections and time slots for all days of the week.
