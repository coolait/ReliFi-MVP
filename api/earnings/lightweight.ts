import { VercelRequest, VercelResponse } from '@vercel/node';
import axios from 'axios';

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:5002';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const { location, date, startTime, endTime, service, lat, lng } = req.query;

    // Build query params
    const params: any = {};
    if (location) params.location = location;
    if (date) params.date = date;
    if (startTime) params.startTime = startTime;
    if (endTime) params.endTime = endTime;
    if (service) params.service = service;
    if (lat) params.lat = lat;
    if (lng) params.lng = lng;

    // Call Python lightweight API
    const response = await axios.get(`${PYTHON_API_URL}/api/earnings/lightweight`, {
      params,
      timeout: 5000 // 5 second timeout (should be < 50ms)
    });

    res.json(response.data);
  } catch (error: any) {
    console.error('Error calling Python lightweight API:', error.message);

    // Fallback to basic estimates
    const hour = parseInt(req.query.startTime?.toString().split(':')[0] || '9');
    const formatTime = (h: number) => {
      if (h === 0) return '12:00 AM';
      if (h < 12) return `${h}:00 AM`;
      if (h === 12) return '12:00 PM';
      return `${h - 12}:00 PM`;
    };

    const fallbackData = {
      location: req.query.location || req.query.lat ? `${req.query.lat},${req.query.lng}` : 'San Francisco',
      date: req.query.date || new Date().toISOString().split('T')[0],
      timeSlot: `${formatTime(hour)} - ${formatTime(hour + 1)}`,
      hour: hour,
      predictions: [
        {
          service: 'Uber',
          min: 20,
          max: 30,
          hotspot: 'Downtown Core',
          demandScore: 0.75,
          tripsPerHour: 2.0,
          surgeMultiplier: 1.0,
          color: '#4285F4',
          startTime: formatTime(hour),
          endTime: formatTime(hour + 1)
        },
        {
          service: 'Lyft',
          min: 18,
          max: 28,
          hotspot: 'Downtown Core',
          demandScore: 0.72,
          tripsPerHour: 1.9,
          surgeMultiplier: 1.0,
          color: '#FF00BF',
          startTime: formatTime(hour),
          endTime: formatTime(hour + 1)
        },
        {
          service: 'DoorDash',
          min: 16,
          max: 26,
          hotspot: 'Restaurant Districts',
          demandScore: 0.70,
          tripsPerHour: 2.5,
          surgeMultiplier: 1.0,
          color: '#FFD700',
          startTime: formatTime(hour),
          endTime: formatTime(hour + 1)
        }
      ],
      metadata: {
        lightweight: true,
        fallback: true
      }
    };

    res.json(fallbackData);
  }
}

