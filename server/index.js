const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json());

// Mock data for gig opportunities
const mockGigData = {
  'monday': {
    '6': [
      { service: 'Uber', startTime: '6:00 AM', endTime: '7:00 AM', projectedEarnings: '$25 - $35', color: '#4285F4' },
      { service: 'Lyft', startTime: '6:00 AM', endTime: '7:00 AM', projectedEarnings: '$22 - $32', color: '#4285F4' },
      { service: 'DoorDash', startTime: '6:00 AM', endTime: '7:00 AM', projectedEarnings: '$18 - $28', color: '#FFD700' }
    ],
    '7': [
      { service: 'Uber', startTime: '7:00 AM', endTime: '8:00 AM', projectedEarnings: '$35 - $45', color: '#4285F4' },
      { service: 'Lyft', startTime: '7:00 AM', endTime: '8:00 AM', projectedEarnings: '$32 - $42', color: '#4285F4' },
      { service: 'Uber Eats', startTime: '7:00 AM', endTime: '8:00 AM', projectedEarnings: '$20 - $30', color: '#E0E0E0' }
    ],
    '8': [
      { service: 'Uber', startTime: '8:00 AM', endTime: '9:00 AM', projectedEarnings: '$40 - $50', color: '#4285F4' },
      { service: 'GrubHub', startTime: '8:00 AM', endTime: '9:00 AM', projectedEarnings: '$25 - $35', color: '#FF6B35' },
      { service: 'DoorDash', startTime: '8:00 AM', endTime: '9:00 AM', projectedEarnings: '$22 - $32', color: '#FFD700' }
    ],
    '9': [
      { service: 'Lyft', startTime: '9:00 AM', endTime: '10:00 AM', projectedEarnings: '$30 - $40', color: '#4285F4' },
      { service: 'Uber', startTime: '9:00 AM', endTime: '10:00 AM', projectedEarnings: '$28 - $38', color: '#4285F4' },
      { service: 'Uber Eats', startTime: '9:00 AM', endTime: '10:00 AM', projectedEarnings: '$18 - $28', color: '#E0E0E0' }
    ],
    '10': [
      { service: 'DoorDash', startTime: '10:00 AM', endTime: '11:00 AM', projectedEarnings: '$25 - $35', color: '#FFD700' },
      { service: 'GrubHub', startTime: '10:00 AM', endTime: '11:00 AM', projectedEarnings: '$22 - $32', color: '#FF6B35' },
      { service: 'Uber Eats', startTime: '10:00 AM', endTime: '11:00 AM', projectedEarnings: '$20 - $30', color: '#E0E0E0' }
    ],
    '11': [
      { service: 'Uber', startTime: '11:00 AM', endTime: '12:00 PM', projectedEarnings: '$35 - $45', color: '#4285F4' },
      { service: 'Lyft', startTime: '11:00 AM', endTime: '12:00 PM', projectedEarnings: '$32 - $42', color: '#4285F4' },
      { service: 'DoorDash', startTime: '11:00 AM', endTime: '12:00 PM', projectedEarnings: '$28 - $38', color: '#FFD700' }
    ],
    '12': [
      { service: 'Uber', startTime: '12:00 PM', endTime: '1:00 PM', projectedEarnings: '$45 - $55', color: '#4285F4' },
      { service: 'Lyft', startTime: '12:00 PM', endTime: '1:00 PM', projectedEarnings: '$42 - $52', color: '#4285F4' },
      { service: 'GrubHub', startTime: '12:00 PM', endTime: '1:00 PM', projectedEarnings: '$35 - $45', color: '#FF6B35' }
    ],
    '13': [
      { service: 'DoorDash', startTime: '1:00 PM', endTime: '2:00 PM', projectedEarnings: '$30 - $40', color: '#FFD700' },
      { service: 'Uber Eats', startTime: '1:00 PM', endTime: '2:00 PM', projectedEarnings: '$25 - $35', color: '#E0E0E0' },
      { service: 'Uber', startTime: '1:00 PM', endTime: '2:00 PM', projectedEarnings: '$28 - $38', color: '#4285F4' }
    ],
    '14': [
      { service: 'Lyft', startTime: '2:00 PM', endTime: '3:00 PM', projectedEarnings: '$25 - $35', color: '#4285F4' },
      { service: 'Uber', startTime: '2:00 PM', endTime: '3:00 PM', projectedEarnings: '$22 - $32', color: '#4285F4' },
      { service: 'GrubHub', startTime: '2:00 PM', endTime: '3:00 PM', projectedEarnings: '$20 - $30', color: '#FF6B35' }
    ],
    '15': [
      { service: 'Uber', startTime: '3:00 PM', endTime: '4:00 PM', projectedEarnings: '$30 - $40', color: '#4285F4' },
      { service: 'DoorDash', startTime: '3:00 PM', endTime: '4:00 PM', projectedEarnings: '$25 - $35', color: '#FFD700' },
      { service: 'Lyft', startTime: '3:00 PM', endTime: '4:00 PM', projectedEarnings: '$28 - $38', color: '#4285F4' }
    ],
    '16': [
      { service: 'Lyft', startTime: '4:00 PM', endTime: '5:00 PM', projectedEarnings: '$35 - $45', color: '#4285F4' },
      { service: 'Uber', startTime: '4:00 PM', endTime: '5:00 PM', projectedEarnings: '$32 - $42', color: '#4285F4' },
      { service: 'Uber Eats', startTime: '4:00 PM', endTime: '5:00 PM', projectedEarnings: '$22 - $32', color: '#E0E0E0' }
    ],
    '17': [
      { service: 'Uber', startTime: '5:00 PM', endTime: '6:00 PM', projectedEarnings: '$50 - $60', color: '#4285F4' },
      { service: 'Lyft', startTime: '5:00 PM', endTime: '6:00 PM', projectedEarnings: '$47 - $57', color: '#4285F4' },
      { service: 'DoorDash', startTime: '5:00 PM', endTime: '6:00 PM', projectedEarnings: '$40 - $50', color: '#FFD700' }
    ],
    '18': [
      { service: 'Uber', startTime: '6:00 PM', endTime: '7:00 PM', projectedEarnings: '$55 - $65', color: '#4285F4' },
      { service: 'Lyft', startTime: '6:00 PM', endTime: '7:00 PM', projectedEarnings: '$52 - $62', color: '#4285F4' },
      { service: 'GrubHub', startTime: '6:00 PM', endTime: '7:00 PM', projectedEarnings: '$45 - $55', color: '#FF6B35' }
    ],
    '19': [
      { service: 'DoorDash', startTime: '7:00 PM', endTime: '8:00 PM', projectedEarnings: '$45 - $55', color: '#FFD700' },
      { service: 'Uber Eats', startTime: '7:00 PM', endTime: '8:00 PM', projectedEarnings: '$35 - $45', color: '#E0E0E0' },
      { service: 'Uber', startTime: '7:00 PM', endTime: '8:00 PM', projectedEarnings: '$40 - $50', color: '#4285F4' }
    ],
    '20': [
      { service: 'Lyft', startTime: '8:00 PM', endTime: '9:00 PM', projectedEarnings: '$40 - $50', color: '#4285F4' },
      { service: 'Uber', startTime: '8:00 PM', endTime: '9:00 PM', projectedEarnings: '$38 - $48', color: '#4285F4' },
      { service: 'GrubHub', startTime: '8:00 PM', endTime: '9:00 PM', projectedEarnings: '$32 - $42', color: '#FF6B35' }
    ],
    '21': [
      { service: 'Uber', startTime: '9:00 PM', endTime: '10:00 PM', projectedEarnings: '$35 - $45', color: '#4285F4' },
      { service: 'DoorDash', startTime: '9:00 PM', endTime: '10:00 PM', projectedEarnings: '$30 - $40', color: '#FFD700' },
      { service: 'Lyft', startTime: '9:00 PM', endTime: '10:00 PM', projectedEarnings: '$32 - $42', color: '#4285F4' }
    ],
    '22': [
      { service: 'Lyft', startTime: '10:00 PM', endTime: '11:00 PM', projectedEarnings: '$30 - $40', color: '#4285F4' },
      { service: 'Uber', startTime: '10:00 PM', endTime: '11:00 PM', projectedEarnings: '$28 - $38', color: '#4285F4' },
      { service: 'Uber Eats', startTime: '10:00 PM', endTime: '11:00 PM', projectedEarnings: '$22 - $32', color: '#E0E0E0' }
    ],
    '23': [
      { service: 'Uber', startTime: '11:00 PM', endTime: '12:00 AM', projectedEarnings: '$25 - $35', color: '#4285F4' },
      { service: 'Lyft', startTime: '11:00 PM', endTime: '12:00 AM', projectedEarnings: '$22 - $32', color: '#4285F4' },
      { service: 'DoorDash', startTime: '11:00 PM', endTime: '12:00 AM', projectedEarnings: '$20 - $30', color: '#FFD700' }
    ]
  }
};

// Generate data for all days of the week
const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
const allDaysData = {};

days.forEach(day => {
  allDaysData[day] = mockGigData.monday; // Using Monday data as template for all days
});

// API Routes
app.get('/api/recommendations/:day/:hour', (req, res) => {
  const { day, hour } = req.params;
  const dayData = allDaysData[day.toLowerCase()];
  
  if (!dayData || !dayData[hour]) {
    return res.status(404).json({ error: 'No recommendations found for this time slot' });
  }
  
  res.json({
    day: day,
    hour: hour,
    recommendations: dayData[hour]
  });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'Server is running!' });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
