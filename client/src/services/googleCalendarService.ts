// Google Calendar integration to fetch busy intervals for the current user
// Uses Google Identity Services (GIS) popup flow to avoid CSP issues
// Requires env vars: REACT_APP_GOOGLE_API_KEY, REACT_APP_GOOGLE_CLIENT_ID

export type BusyTime = { start: string; end: string };

let token: string | null = null;
let gapiLoaded = false;

const GAPI_SCRIPT_SRC = 'https://apis.google.com/js/api.js';
const GIS_SCRIPT_SRC = 'https://accounts.google.com/gsi/client';

function loadGapiScript(): Promise<void> {
  if (gapiLoaded) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = GAPI_SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      gapiLoaded = true;
      resolve();
    };
    script.onerror = () => reject(new Error('Failed to load Google API script'));
    document.head.appendChild(script);
  });
}

function loadGISScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if ((window as any).google?.accounts) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = GIS_SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Google Identity Services'));
    document.head.appendChild(script);
  });
}

async function authenticateUser(): Promise<string> {
  const apiKey = process.env.REACT_APP_GOOGLE_API_KEY as string | undefined;
  const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID as string | undefined;
  if (!apiKey || !clientId) {
    throw new Error('Missing Google API credentials. Set REACT_APP_GOOGLE_API_KEY and REACT_APP_GOOGLE_CLIENT_ID.');
  }

  await loadGISScript();
  await loadGapiScript();

  return new Promise((resolve, reject) => {
    // @ts-ignore
    const google = window.google;
    
    // Use Google Identity Services popup flow
    google.accounts.oauth2.initTokenClient({
      client_id: clientId,
      scope: 'https://www.googleapis.com/auth/calendar.readonly',
      callback: (response: { access_token: string }) => {
        if (response.access_token) {
          token = response.access_token;
          resolve(response.access_token);
        } else {
          reject(new Error('Failed to get access token'));
        }
      },
    }).requestAccessToken();
  });
}

async function initGapiClient(accessToken: string): Promise<void> {
  await loadGapiScript();
  
  // @ts-ignore
  const gapi = window.gapi;
  
  await new Promise<void>((resolve, reject) => {
    gapi.load('client', async () => {
      try {
        await gapi.client.init({
          apiKey: process.env.REACT_APP_GOOGLE_API_KEY,
          discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'],
        });
        
        // Set the access token
        gapi.client.setToken({ access_token: accessToken });
        resolve();
      } catch (err) {
        reject(err);
      }
    });
  });
}

export async function fetchBusyIntervals(startIso: string, endIso: string): Promise<BusyTime[]> {
  // Authenticate if we don't have a token
  if (!token) {
    const accessToken = await authenticateUser();
    await initGapiClient(accessToken);
  }

  // @ts-ignore
  const gapi = window.gapi;
  
  // Get user's timezone
  const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  
  const body = {
    timeMin: startIso,
    timeMax: endIso,
    timeZone: userTimezone,
    items: [{ id: 'primary' }]
  };
  
  console.log('📅 Fetching busy intervals:', {
    timeMin: startIso,
    timeMax: endIso,
    timeZone: userTimezone
  });
  
  const resp = await gapi.client.calendar.freebusy.query({ resource: body });
  const calendars = resp.result.calendars || {};
  const primary = calendars['primary'];
  const busy = (primary?.busy || []) as Array<{ start: string; end: string }>;
  
  console.log('📅 Received busy intervals from Google:', busy.length);
  busy.forEach((interval, idx) => {
    console.log(`  ${idx + 1}. ${interval.start} - ${interval.end}`);
  });
  
  return busy.map(b => ({ start: b.start, end: b.end }));
}

export function computeWeekRange(currentWeek: Date): { start: Date; end: Date } {
  const start = new Date(currentWeek);
  start.setDate(currentWeek.getDate() - currentWeek.getDay());
  start.setHours(0, 0, 0, 0);
  const end = new Date(start);
  end.setDate(start.getDate() + 7);
  return { start, end };
}

export function busyIntervalsToSlotKeys(busy: BusyTime[], weekStart: Date): Set<string> {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  
  // Calculate start of week in local time (Sunday at 00:00)
  const startOfWeek = new Date(weekStart);
  startOfWeek.setDate(weekStart.getDate() - weekStart.getDay());
  startOfWeek.setHours(0, 0, 0, 0);
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(startOfWeek.getDate() + 7);

  const result = new Set<string>();

  // Our grid hours are 6..23 inclusive (local time)
  const gridHours = Array.from({ length: 18 }, (_, i) => i + 6);

  // Precompute date for each day index in local timezone
  const dayDateAtHour = (dayIndex: number, hour: number): Date => {
    const d = new Date(startOfWeek);
    d.setDate(startOfWeek.getDate() + dayIndex);
    d.setHours(hour, 0, 0, 0);
    return d;
  };

  // Convert Google Calendar busy intervals to local time milliseconds
  const busyIntervals = busy.map(interval => {
    // Google Calendar returns ISO strings (may be in UTC or local time)
    // Parse them and convert to local time for comparison
    const start = new Date(interval.start);
    const end = new Date(interval.end);
    return {
      start: start.getTime(),
      end: end.getTime()
    };
  });

  console.log('📅 Processing busy intervals:', busyIntervals.length);
  console.log('📅 Week range:', {
    start: startOfWeek.toLocaleString(),
    end: endOfWeek.toLocaleString()
  });

  for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
    for (const hour of gridHours) {
      const slotStart = dayDateAtHour(dayIndex, hour);
      const slotEnd = dayDateAtHour(dayIndex, hour + 1);
      const slotStartMs = slotStart.getTime();
      const slotEndMs = slotEnd.getTime();

      let overlaps = false;
      for (const interval of busyIntervals) {
        // Check if busy interval overlaps with this time slot
        // Overlap occurs if: interval.end > slotStart AND interval.start < slotEnd
        if (interval.end > slotStartMs && interval.start < slotEndMs) {
          overlaps = true;
          console.log(`✅ Found overlap: ${days[dayIndex]} ${hour}:00 - ${hour + 1}:00 with interval ${new Date(interval.start).toLocaleString()} - ${new Date(interval.end).toLocaleString()}`);
          break;
        }
      }
      if (overlaps) {
        const dayName = days[dayIndex];
        result.add(`${dayName}-${hour}`);
      }
    }
  }

  console.log(`📅 Total busy slots: ${result.size}`);
  return result;
}

