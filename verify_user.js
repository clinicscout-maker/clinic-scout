// Verification script to check if test user exists in Firestore
// Run with: node verify_user.js

const admin = require('firebase-admin');

// Initialize Firebase Admin
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

async function verifyUser() {
    try {
        console.log('🔍 Searching for user: tinschan4@gmail.com\n');

        const usersRef = db.collection('users');
        const query = usersRef.where('email', '==', 'tinschan4@gmail.com').limit(1);
        const snapshot = await query.get();

        if (snapshot.empty) {
            console.log('❌ User NOT found in Firestore');
            console.log('Please create the user first using Firebase Console or create_test_user.js\n');
            process.exit(1);
        }

        const doc = snapshot.docs[0];
        const data = doc.data();

        console.log('✅ User FOUND in Firestore!\n');
        console.log('📄 Document ID:', doc.id);
        console.log('📧 Email:', data.email);
        console.log('📱 Phone:', data.phoneNumber || 'Not set');
        console.log('💎 Premium:', data.isPremium ? 'YES ✅' : 'NO ❌');
        console.log('🔄 Subscription:', data.isSubscription ? 'YES' : 'NO');
        console.log('📍 Areas:', data.areas || []);
        console.log('🌍 Province:', data.province || 'Not set');
        console.log('🗣️  Languages:', data.languages || []);
        console.log('💰 Last Payment:', data.lastPaymentAmount || 'N/A');
        console.log('📅 Created:', data.createdAt?.toDate?.() || 'N/A');
        console.log('📅 Premium Since:', data.premiumSince?.toDate?.() || 'N/A');

        console.log('\n✅ Verification Complete!');
        console.log('\n🧪 Test Login Flow:');
        console.log('1. Go to http://localhost:3002');
        console.log('2. Enter email: tinschan4@gmail.com');
        console.log('3. Click "Send Magic Link"');
        console.log('4. Check email and click the link');
        console.log('5. Expected: Shows "You\'re Active!" + ALL clinics unlocked\n');

        process.exit(0);
    } catch (error) {
        console.error('❌ Error verifying user:', error);
        process.exit(1);
    }
}

verifyUser();
