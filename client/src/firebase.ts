import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

// Client-side Firebase SDK only – do NOT use firebase-admin in the browser
// Admin access should be used on the server (e.g., Vercel functions)

const firebaseConfig = {
    apiKey: process.env.REACT_APP_FIREBASE_API_KEY as string,
    authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN as string,
    projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID as string,
    storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET as string,
    messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID as string,
    appId: process.env.REACT_APP_FIREBASE_APP_ID as string,
    measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID as string
  }

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
export const db = getFirestore(app);

export default app;
