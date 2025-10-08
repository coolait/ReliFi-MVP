import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

// Client-side Firebase SDK only – do NOT use firebase-admin in the browser
// Admin access should be used on the server (e.g., Vercel functions)

const firebaseConfig = {
    apiKey: "AIzaSyAqEHJ_pPJ6kKM-HLpmWtGQj1foUoybeGs",
    authDomain: "relifi.firebaseapp.com",
    projectId: "relifi",
    storageBucket: "relifi.firebasestorage.app",
    messagingSenderId: "645555164041",
    appId: "1:645555164041:web:4a66bc0379bce346f1c758",
    measurementId: "G-5YVYKV5PXD"
  }

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
export const db = getFirestore(app);

export default app;
