// Lightweight Google Calendar integration to fetch busy intervals for the current user
// Uses gapi client. Requires env vars: REACT_APP_GOOGLE_API_KEY, REACT_APP_GOOGLE_CLIENT_ID

type BusyTime = { start: string; end: string };

let gapiLoaded = false;
let clientInitialized = false;

const GAPI_SCRIPT_SRC = 'https://apis.google.com/js/api.js';

function loadGapiScript(): Promise<void> {
  if (gapiLoaded) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = GAPI_SCRIPT_SRC;
    script.async = true;
    script.onload = () => {
      gapiLoaded = true;
      resolve();
    };
    script.onerror = () => reject(new Error('Failed to load Google API script'));
    document.body.appendChild(script);
  });
}

async function initClient(): Promise<void> {
  if (clientInitialized) return;
  const apiKey = process.env.REACT_APP_GOOGLE_API_KEY as string | undefined;
  const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID as string | undefined;
  if (!apiKey || !clientId) {
    throw new Error('Missing Google API credentials. Set REACT_APP_GOOGLE_API_KEY and REACT_APP_GOOGLE_CLIENT_ID.');
  }

  // @ts-ignore gapi is injected by the script
  const gapi = (window as any).gapi;
  await new Promise<void>((resolve, reject) => {
    gapi.load('client:auth2', async () => {
      try {
        await gapi.client.init({
          apiKey,
          clientId,
          discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'],
          scope: 'https://www.googleapis.com/auth/calendar.readonly'
        });
        clientInitialized = true;
        resolve();
      } catch (err) {
        reject(err);
      }
    });
  });
}

async function ensureSignedIn(): Promise<void> {
  // @ts-ignore
  const gapi = (window as any).gapi;
  const auth = gapi.auth2.getAuthInstance();
  if (!auth.isSignedIn.get()) {
    await auth.signIn();
  }
}

export async function fetchBusyIntervals(startIso: string, endIso: string): Promise<BusyTime[]> {
  await loadGapiScript();
  await initClient();
  await ensureSignedIn();

  // @ts-ignore
  const gapi = (window as any).gapi;
  const body = {
    timeMin: startIso,
    timeMax: endIso,
    items: [{ id: 'primary' }]
  };
  const resp = await gapi.client.calendar.freebusy.query({ resource: body });
  const calendars = resp.result.calendars || {};
  const primary = calendars['primary'];
  const busy = (primary?.busy || []) as Array<{ start: string; end: string }>;
  return busy.map(b => ({ start: b.start, end: b.end }));
}

export function mapBusyToHourKeys(weekStart: Date): Set<string> {
  // This function requires the busy intervals; kept separate for clarity.
  return new Set();
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
  const startOfWeek = new Date(weekStart);
  startOfWeek.setHours(0, 0, 0, 0);
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(endOfWeek.getDate() + 7);

  const result = new Set<string>();

  // Our grid hours are 6..23 inclusive
  const gridHours = Array.from({ length: 18 }, (_, i) => i + 6);

  // Precompute date for each day index
  const dayDateAtHour = (dayIndex: number, hour: number): Date => {
    const d = new Date(startOfWeek);
    d.setDate(startOfWeek.getDate() + dayIndex);
    d.setHours(hour, 0, 0, 0);
    return d;
  };

  const clamp = (d: Date) => Math.max(startOfWeek.getTime(), Math.min(endOfWeek.getTime(), d.getTime()));

  for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
    for (const hour of gridHours) {
      const slotStart = dayDateAtHour(dayIndex, hour);
      const slotEnd = dayDateAtHour(dayIndex, hour + 1);
      const slotStartMs = slotStart.getTime();
      const slotEndMs = slotEnd.getTime();

      let overlaps = false;
      for (const interval of busy) {
        const bStartMs = clamp(new Date(interval.start));
        const bEndMs = clamp(new Date(interval.end));
        if (bEndMs > slotStartMs && bStartMs < slotEndMs) {
          overlaps = true;
          break;
        }
      }
      if (overlaps) {
        const dayName = days[dayIndex];
        result.add(`${dayName}-${hour}`);
      }
    }
  }

  return result;
}



