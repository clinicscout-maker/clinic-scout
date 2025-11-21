# 🏥 Clinic Scout

**Real-time Family Doctor Availability Tracker for Canada**

[![Next.js](https://img.shields.io/badge/Next.js-15.0-black?logo=next.js)](https://nextjs.org/)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore%20%2B%20Auth-orange?logo=firebase)](https://firebase.google.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?logo=typescript)](https://www.typescriptlang.org/)

A production-grade SaaS platform that monitors **250+ family doctor clinics** across Ontario, British Columbia, and Alberta in real-time, sending instant SMS alerts when appointments become available.

---

## ✨ Features

- **🔴 Live Status Monitoring**: Real-time tracking of clinic availability (Open/Waitlist/Closed)
- **📱 Instant SMS Alerts**: Twilio-powered notifications the moment a spot opens
- **🗺️ Multi-Province Support**: Coverage across ON, BC, and AB with city-level filtering
- **🎯 Smart Filtering**: Filter by province, location, and status
- **💳 Ko-fi Integration**: Seamless premium membership with webhook-based activation
- **📊 Social Proof**: Community-driven voting system for clinic reliability
- **🔐 Secure Authentication**: Firebase Anonymous Auth with phone number storage
- **⚡ Optimized Performance**: Next.js 15 with server-side rendering and edge caching

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18.x or higher
- **npm** or **yarn**
- **Firebase Project** (Firestore + Authentication enabled)
- **Twilio Account** (for SMS alerts)
- **Ko-fi Account** (for payment processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/clinicscout-maker/clinic-scout.git
   cd clinic-scout
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**

   Create a `.env.local` file in the root directory:

   ```env
   # Firebase Configuration
   NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

5. **Build for production**
   ```bash
   npm run build
   npm start
   ```

---

## 🏗️ Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Modern icon library
- **clsx** - Conditional class management

### Backend & Services
- **Firebase Firestore** - Real-time NoSQL database
- **Firebase Authentication** - Anonymous auth with phone storage
- **Twilio** - SMS notification delivery
- **Ko-fi** - Payment processing and webhooks
- **Google Cloud Functions** - Serverless webhook handlers

### DevOps
- **Vercel** - Deployment and hosting
- **GitHub** - Version control
- **Playwright** - Web scraping automation
- **Google Gemini AI** - Intelligent clinic status parsing

---

## 📁 Project Structure

```
clinic-scout/
├── src/
│   ├── app/
│   │   ├── page.tsx          # Main landing page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── Auth.tsx           # Authentication flow
│   │   ├── ClinicList.tsx     # Clinic grid with filters
│   │   └── PreferencesForm.tsx # User preference settings
│   └── lib/
│       └── firebase.ts        # Firebase initialization
├── scraper/
│   ├── main.py                # Clinic scraper with Gemini AI
│   └── notifications.py       # Twilio SMS handler
├── webhook_service/
│   └── main.py                # Ko-fi payment webhook
├── public/                    # Static assets
└── package.json               # Dependencies
```

---

## 🔧 Configuration

### Firebase Setup
1. Enable **Anonymous Authentication** in Firebase Console
2. Create Firestore collections:
   - `users` - User profiles and preferences
   - `clinics` - Clinic data and status

### Twilio Setup
1. Get your Account SID and Auth Token
2. Purchase a phone number
3. Add credentials to environment variables

### Ko-fi Webhook
1. Deploy webhook to Google Cloud Functions:
   ```bash
   ./deploy_webhook.sh your-gcp-project-id
   ```
2. Copy the function URL and verification token
3. Add to Ko-fi Dashboard → Webhooks

---

## 🚢 Deployment

### Deploy to Vercel

1. **Connect GitHub repository** to Vercel
2. **Add environment variables** in Vercel Dashboard
3. **Deploy**:
   ```bash
   vercel --prod
   ```

### Deploy Webhook to Google Cloud Functions

```bash
chmod +x deploy_webhook.sh
./deploy_webhook.sh your-gcp-project-id
```

---

## 📊 Scraper Setup

The scraper runs periodically to update clinic statuses:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run scraper
python scraper/main.py
```

**Environment variables needed:**
- `GEMINI_API_KEY` - Google AI API key
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Firebase service account JSON

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 🙏 Acknowledgments

- **Ko-fi** for payment infrastructure
- **Twilio** for SMS delivery
- **Google Gemini AI** for intelligent status parsing
- **Vercel** for seamless deployment

---

## 📞 Support

For issues or questions, please open a GitHub issue or contact us at [support@clinicscout.ca](mailto:support@clinicscout.ca).

---

**Built with ❤️ for Canadians seeking family doctors**
