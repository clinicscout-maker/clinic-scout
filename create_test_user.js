// Quick script to create a test user in Firestore
// Run with: node create_test_user.js

const admin = require('firebase-admin');

// Initialize Firebase Admin (requires service account key)
// Download from: Firebase Console > Project Settings > Service Accounts
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

async function createTestUser() {
    try {
        const userRef = db.collection('users').doc(); // Auto-generate ID

        await userRef.set({
            email: 'tinschan4@gmail.com',
            phoneNumber: '+14379733359',
            isPremium: true,
            isSubscription: true,
            premiumSince: admin.firestore.FieldValue.serverTimestamp(),
            createdAt: admin.firestore.FieldValue.serverTimestamp(),
            areas: ['Toronto'],
            province: 'ON',
            languages: ['English'],
            lastPaymentAmount: '5.00',
            lastPaymentDate: new Date().toISOString()
        });

        console.log('✅ Test user created successfully!');
        console.log('Document ID:', userRef.id);
        console.log('Email: tinschan4@gmail.com');
        console.log('Phone: +14379733359');
        console.log('Premium: true');

        process.exit(0);
    } catch (error) {
        console.error('❌ Error creating user:', error);
        process.exit(1);
    }
}

createTestUser();
