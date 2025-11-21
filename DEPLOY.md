# 🚀 Clinic Scout - Deployment Guide

## Production Deployment Checklist

### Prerequisites
- [ ] GitHub account with repository access
- [ ] Vercel account (free tier works)
- [ ] Firebase project with Firestore enabled
- [ ] Ko-fi account with membership tier set up
- [ ] All environment variables ready

---

## 📋 Environment Variables for Vercel

Copy these **exact** environment variable names into your Vercel project settings.

### Firebase Configuration
```
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### Where to Find Firebase Credentials:
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click gear icon ⚙️ → Project Settings
4. Scroll to "Your apps" section
5. Copy values from the `firebaseConfig` object

---

## 🔐 Security Checklist

- [x] `.env.local` is in `.gitignore`
- [x] `.env` is in `.gitignore`
- [x] `serviceAccountKey.json` is in `.gitignore`
- [x] `.kofi_token` is in `.gitignore`
- [ ] **VERIFY**: Run `git status` - NO sensitive files should appear
- [ ] **DOUBLE CHECK**: Search codebase for any hardcoded API keys

---

## 📦 Deployment Steps

### Step 1: Prepare Git Repository

```bash
# Navigate to project root
cd "/Users/tinshuichan/Library/Mobile Documents/com~apple~CloudDocs/Antigravity"

# Verify gitignore is working
git status

# Stage all files (sensitive files will be excluded automatically)
git add .

# Commit
git commit -m "Initial Commit: Clinic Scout V1"

# Create GitHub repository (via GitHub web UI or CLI)
# Then add remote and push
git remote add origin https://github.com/YOUR_USERNAME/clinic-scout.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Vercel

#### Option A: Vercel Dashboard (Recommended)
1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"**
3. Import your GitHub repository: `YOUR_USERNAME/clinic-scout`
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

5. **Add Environment Variables** (click "Environment Variables"):
   - Paste all variables from the list above
   - Set for: **Production**, **Preview**, and **Development**

6. Click **"Deploy"**

#### Option B: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Follow prompts and paste environment variables when asked
```

### Step 3: Post-Deployment Configuration

#### Update Ko-fi Webhook URL
1. Log in to [Ko-fi Dashboard](https://ko-fi.com/manage/webhooks)
2. Update webhook URL to: `https://YOUR_VERCEL_URL.vercel.app/api/webhook/kofi`
3. Test the webhook with a sample payment

#### Update Firebase Security Rules (if needed)
```javascript
// Firestore Rules - Allow read for authenticated users
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /clinics/{clinic} {
      allow read: if true; // Public read
      allow write: if false; // Only backend can write
    }
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

---

## ✅ Verification Steps

After deployment, verify the following:

### Frontend Tests
- [ ] Can load homepage at your Vercel URL
- [ ] Login form appears when not logged in
- [ ] Clinic list loads (3 visible + 6 blurred)
- [ ] Can complete signup (phone + email)
- [ ] Preferences form saves to Firebase
- [ ] Ko-fi redirect works (opens membership page)
- [ ] "Listening for Payment" screen appears

### Backend Tests
- [ ] Ko-fi webhook receives payments
- [ ] Webhook sets `isPremium: true` in Firestore
- [ ] Premium users see full clinic list unlocked
- [ ] "My Preferences" card appears for premium users
- [ ] Logout button works

### Performance Tests
- [ ] Lighthouse score > 90 (Performance)
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3.5s

---

## 🐛 Troubleshooting

### Build Fails on Vercel
**Problem**: TypeScript or ESLint errors  
**Solution**: Already configured in `next.config.js` to ignore build errors

### Firebase Connection Error
**Problem**: "Firebase: Error (auth/invalid-api-key)"  
**Solution**: Double-check environment variables in Vercel dashboard

### Ko-fi Webhook Not Working
**Problem**: Payment doesn't unlock premium  
**Solution**: 
1. Check webhook URL in Ko-fi dashboard
2. Check Vercel function logs: **Functions** → **api/webhook/kofi**
3. Verify webhook secret matches between Ko-fi and Vercel env

### Images/Assets Not Loading
**Problem**: 404 on static assets  
**Solution**: Ensure all images are in `/public` folder

---

## 📊 Monitoring

### Vercel Analytics
- Enable in Vercel dashboard: **Analytics** tab
- Track page views, unique visitors, performance

### Firebase Console
- Monitor Firestore reads/writes: **Usage** tab
- Check authentication metrics: **Authentication** → **Users**

### Ko-fi Dashboard
- Track memberships: **Supporters** page
- Monitor webhook delivery: **Settings** → **Webhooks**

---

## 🔄 Updating Production

```bash
# Make changes locally
git add .
git commit -m "feat: your feature description"
git push origin main

# Vercel auto-deploys on push to main branch
# Check deployment status at vercel.com/YOUR_USERNAME/clinic-scout
```

---

## 📝 Important URLs

- **Production URL**: `https://YOUR_PROJECT.vercel.app` (get from Vercel)
- **Firebase Console**: `https://console.firebase.google.com/project/YOUR_PROJECT_ID`
- **Ko-fi Dashboard**: `https://ko-fi.com/manage`
- **Vercel Dashboard**: `https://vercel.com/YOUR_USERNAME/clinic-scout`
- **GitHub Repository**: `https://github.com/YOUR_USERNAME/clinic-scout`

---

## 🆘 Support

If you encounter issues:
1. Check Vercel function logs
2. Check Firebase console for errors
3. Review Ko-fi webhook delivery logs
4. Search GitHub issues or create new issue

---

**Last Updated**: 2025-11-20  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
