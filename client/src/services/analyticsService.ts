import { doc, getDoc, setDoc, updateDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '../firebase';

export interface GcalClickData {
  clickCount: number;
  lastClicked: any; // Firestore timestamp
  totalClicks: number;
}

export const trackGcalClick = async (service: string, day: string, hour: string) => {
  console.log('🔥 Firebase: Starting to track click...', { service, day, hour });
  
  try {
    const docRef = doc(db, 'Clicks Across', 'Gcal Clicks');
    console.log('🔥 Firebase: Document reference created');
    
    const docSnap = await getDoc(docRef);
    console.log('🔥 Firebase: Document snapshot retrieved', { exists: docSnap.exists() });

    // Check if this is a new user session (first click this page load)
    const sessionKey = 'gcal-click-tracked';
    const hasClickedThisSession = sessionStorage.getItem(sessionKey);
    const isNewSession = !hasClickedThisSession;
    
    console.log('🔥 Firebase: Session check:', { 
      sessionKey, 
      hasClickedThisSession,
      isNewSession,
      sessionStorageAvailable: typeof sessionStorage !== 'undefined'
    });
    
    if (docSnap.exists()) {
      // Document exists, update the count
      const currentData = docSnap.data();
      console.log('🔥 Firebase: Current data:', currentData);
      
      const currentClickCount = currentData.clickCount || 0;
      const currentTotalClicks = currentData.totalClicks || 0;
      
      // Only increment clickCount for new user sessions
      const newCount = isNewSession ? currentClickCount + 1 : currentClickCount;
      const newTotalClicks = currentTotalClicks + 1; // Always increment totalClicks
      
      console.log('🔥 Firebase: Updating with new values:', { 
        newCount, 
        newTotalClicks, 
        isNewSession,
        service, 
        day, 
        hour 
      });
      
      await updateDoc(docRef, {
        clickCount: newCount,
        lastClicked: serverTimestamp(),
        totalClicks: newTotalClicks,
        lastService: service,
        lastDay: day,
        lastHour: hour
      });
      
      // Mark this session as tracked
      if (isNewSession) {
        sessionStorage.setItem(sessionKey, 'true');
      }
      
      console.log('✅ Firebase: Google Calendar click tracked successfully. Total clicks:', newTotalClicks, 'Session clicks:', newCount);
    } else {
      // Document doesn't exist, create it
      console.log('🔥 Firebase: Document does not exist, creating new one');
      
      await setDoc(docRef, {
        clickCount: 1,
        lastClicked: serverTimestamp(),
        totalClicks: 1,
        lastService: service,
        lastDay: day,
        lastHour: hour,
        createdAt: serverTimestamp()
      });
      
      // Mark this session as tracked
      sessionStorage.setItem(sessionKey, 'true');
      
      console.log('✅ Firebase: Google Calendar click tracking initialized. First click recorded.');
    }
  } catch (error) {
    console.error('❌ Firebase: Error tracking Google Calendar click:', error);
    console.error('❌ Firebase: Error details:', {
      message: error instanceof Error ? error.message : String(error),
      code: error instanceof Error && 'code' in error ? (error as any).code : 'unknown',
      stack: error instanceof Error ? error.stack : 'no stack trace'
    });
  }
};

export const getGcalClickStats = async (): Promise<GcalClickData | null> => {
  try {
    const docRef = doc(db, 'Clicks Across', 'Gcal Clicks');
    const docSnap = await getDoc(docRef);
    
    if (docSnap.exists()) {
      return docSnap.data() as GcalClickData;
    }
    return null;
  } catch (error) {
    console.error('Error getting Google Calendar click stats:', error instanceof Error ? error.message : String(error));
    return null;
  }
};

// Test function to verify Firebase connection
export const testFirebaseConnection = async () => {
  console.log('🔥 Firebase: Testing connection...');
  try {
    const docRef = doc(db, 'Clicks Across', 'Gcal Clicks');
    const docSnap = await getDoc(docRef);
    console.log('✅ Firebase: Connection successful!', { exists: docSnap.exists() });
    return true;
  } catch (error) {
    console.error('❌ Firebase: Connection failed:', error instanceof Error ? error.message : String(error));
    return false;
  }
};

// Function to reset session tracking (for testing)
export const resetSessionTracking = () => {
  const sessionKey = 'gcal-click-tracked';
  sessionStorage.removeItem(sessionKey);
  console.log('🔄 Session tracking reset - next click will count as new session');
};
