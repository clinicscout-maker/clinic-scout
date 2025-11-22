"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { User, isSignInWithEmailLink, signInWithEmailLink } from "firebase/auth";
import { doc, getDoc, setDoc, collection, getDocs, query, where, limit, onSnapshot } from "firebase/firestore";
import { db, auth } from "@/lib/firebase";
import Auth from "@/components/Auth";
import ClinicList from "@/components/ClinicList";
import PreferencesForm from "@/components/PreferencesForm";
import { Zap, Activity, Settings, MapPin, Clock, Sparkles, Mail } from "lucide-react";

// Real Ko-fi membership tier direct link
const KOFI_LINK = "https://ko-fi.com/summary/2fa9d8df-c028-400e-bf9b-d3b065fab8cc";
// Ko-fi page for subscription management (users can contact you here)
const KOFI_MANAGE_LINK = "https://ko-fi.com/clinicscout";

// Helper function to calculate time ago
function getTimeAgo(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
}

export default function Home() {
    const [user, setUser] = useState<User | null>(null);
    const [isPremium, setIsPremium] = useState(false);
    const [hasProfile, setHasProfile] = useState(false);
    const [isWaitingForPayment, setIsWaitingForPayment] = useState(false);
    const [clinicCount, setClinicCount] = useState(0);
    const [showPreferencesModal, setShowPreferencesModal] = useState(false);
    const [userData, setUserData] = useState<any>(null);
    const [lastChecked, setLastChecked] = useState<Date | null>(null);

    useEffect(() => {
        if (!user) {
            setUserData(null);
            setIsPremium(false);
            setHasProfile(false);
            setIsWaitingForPayment(false);
            return;
        }

        const docRef = doc(db, "users", user.uid);
        // Real-time listener for user data (premium status + preferences)
        const unsubscribe = onSnapshot(docRef, (docSnap) => {
            if (docSnap.exists()) {
                const data = docSnap.data();
                setUserData(data);
                if (data.isPremium) {
                    setIsPremium(true);
                    setIsWaitingForPayment(false); // Payment received!
                } else {
                    setIsPremium(false);
                }
                // Fix: Check for areas (array) instead of area (singular)
                if (data.areas && data.areas.length > 0) setHasProfile(true);
                else setHasProfile(false);
            } else {
                setUserData(null);
                setIsPremium(false);
                setHasProfile(false);
            }
        });

        return () => unsubscribe();
    }, [user]);

    useEffect(() => {
        const fetchClinicCount = async () => {
            try {
                const snapshot = await getDocs(collection(db, "clinics"));
                setClinicCount(snapshot.size);
            } catch (error) {
                console.error("Error fetching clinic count:", error);
            }
        };
        fetchClinicCount();
    }, []);

    // Handle Email Link Sign-in
    useEffect(() => {
        if (isSignInWithEmailLink(auth, window.location.href)) {
            let email = window.localStorage.getItem('emailForSignIn');
            if (!email) {
                // User opened link on different device. Ask for email.
                email = window.prompt('Please provide your email for confirmation');
            }

            if (email) {
                signInWithEmailLink(auth, email, window.location.href)
                    .then(async (result) => {
                        // Clear email from storage
                        window.localStorage.removeItem('emailForSignIn');

                        // STEP 1: Check if user document exists by UID
                        const userRef = doc(db, "users", result.user.uid);
                        const userSnap = await getDoc(userRef);

                        if (!userSnap.exists()) {
                            // STEP 2: User document doesn't exist by UID
                            // Check if there's existing data by email (e.g., from webhook before login)
                            console.log("🔍 Checking for existing user data by email:", result.user.email);

                            const usersRef = collection(db, "users");
                            const q = query(usersRef, where("email", "==", result.user.email), limit(1));
                            const querySnapshot = await getDocs(q);

                            if (!querySnapshot.empty) {
                                // FOUND: Existing user data with this email
                                const existingDoc = querySnapshot.docs[0];
                                const existingData = existingDoc.data();

                                console.log("✅ Found existing user data! Linking to new UID:", result.user.uid);

                                // Create new document with UID, preserving existing data
                                await setDoc(userRef, {
                                    ...existingData,
                                    uid: result.user.uid,
                                    linkedAt: new Date()
                                });

                                // Optional: Delete old document to avoid duplicates
                                // await deleteDoc(doc(db, "users", existingDoc.id));

                            } else {
                                // NOT FOUND: Create new user document
                                console.log("✅ Creating new user document for:", result.user.email);
                                await setDoc(userRef, {
                                    email: result.user.email,
                                    createdAt: new Date(),
                                    isPremium: false,
                                    areas: [],
                                    province: 'ON'
                                });
                            }
                        } else {
                            console.log("✅ User document already exists");
                        }

                        setUser(result.user);
                    })
                    .catch((error) => {
                        console.error("Error signing in with email link", error);
                        alert("Error signing in with email link: " + error.message);
                    });
            }
        }
    }, []);

    const paymentUrl = KOFI_LINK;

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
            {/* Sticky Header */}
            <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm">
                <div className="w-full px-4 md:px-8 py-4 flex items-center justify-between lg:max-w-7xl lg:mx-auto">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-teal-600 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
                            <Activity className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-lg font-bold text-slate-900">Clinic Scout</h1>
                            <p className="text-xs text-slate-500">Medical Availability Tracker</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 bg-teal-50 border border-teal-200 rounded-full px-4 py-2">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-500 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-600"></span>
                            </span>
                            <span className="text-xs font-bold text-teal-700">Monitoring {clinicCount}+ Clinics Live</span>
                        </div>
                        {user && (
                            <button
                                onClick={() => {
                                    auth.signOut();
                                    window.location.reload();
                                }}
                                className="text-xs text-slate-500 hover:text-slate-700 underline"
                            >
                                Logout
                            </button>
                        )}
                    </div>
                </div>
            </header>

            <main className="w-full px-4 pt-6 pb-8 md:px-8 md:pt-12 lg:max-w-7xl lg:mx-auto">
                <div className="grid gap-6 lg:gap-12 lg:grid-cols-12 w-full">

                    {/* LEFT COLUMN: Action Zone (Sticky) */}
                    <div className="order-1 lg:col-span-5 lg:sticky lg:top-28 space-y-8">

                        {/* Hero Text (Only show if not logged in) */}
                        {!user && (
                            <div className="space-y-6">
                                <div className="flex flex-wrap gap-3">
                                    <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-bold border border-blue-100">
                                        Trusted by 1,000+ Canadians
                                    </span>
                                    <span className="px-3 py-1 rounded-full bg-purple-50 text-purple-700 text-xs font-bold border border-purple-100 flex items-center gap-1">
                                        <Sparkles className="w-3 h-3" />
                                        AI-Powered Real-time Scanning
                                    </span>
                                </div>
                                <h1 className="text-4xl md:text-6xl font-black tracking-tight text-slate-900 leading-tight">
                                    Stop Searching. <span className="text-blue-600">Start Seeing a Doctor.</span>
                                </h1>
                                <p className="text-lg text-slate-600 leading-relaxed">
                                    Don't Miss the Next Open Spot. Our <span className="font-bold text-slate-900">AI agents</span> monitor 500+ clinics 24/7 and interpret waitlist status instantly, sending you an SMS the second a spot opens.
                                </p>
                            </div>
                        )}

                        {/* Step 1: Login (User is null) */}
                        {!user && (
                            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 overflow-hidden animate-fade-in">
                                <Auth onLogin={setUser} />
                            </div>
                        )}

                        {/* Step 2: Setup & Pay - Show PreferencesForm or Listening state */}
                        {user && !isPremium && (
                            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 p-6 animate-fade-in">
                                {!isWaitingForPayment ? (
                                    <>
                                        <div className="mb-4">
                                            <h2 className="text-2xl font-bold text-slate-900 mb-2">Setup & Pay</h2>
                                            <p className="text-sm text-slate-500">Set your preferences and join premium</p>
                                        </div>
                                        <PreferencesForm
                                            user={user}
                                            mode="setup"
                                            onComplete={(email: string) => {
                                                // Redirect to Ko-fi with email
                                                setIsWaitingForPayment(true);
                                                const kofiUrl = `${KOFI_LINK}?email=${encodeURIComponent(email)}`;
                                                window.open(kofiUrl, '_blank', 'noopener,noreferrer');
                                            }}
                                        />
                                    </>
                                ) : (
                                    // Listening for Payment UI
                                    <div className="text-center py-8">
                                        <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white mx-auto mb-6 shadow-xl shadow-blue-500/30 relative">
                                            <Activity className="w-8 h-8" />
                                            <span className="absolute -top-1 -right-1 flex h-4 w-4">
                                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                                                <span className="relative inline-flex rounded-full h-4 w-4 bg-blue-500"></span>
                                            </span>
                                        </div>
                                        <h2 className="text-2xl font-bold text-slate-900 mb-3">Listening for Payment...</h2>
                                        <p className="text-slate-500 mb-6">
                                            Complete your Ko-fi payment in the new tab. We'll activate your account automatically!
                                        </p>

                                        <div className="bg-amber-50 rounded-xl p-4 border border-amber-100 mb-6 max-w-md mx-auto">
                                            <p className="text-sm text-amber-900 mb-2">
                                                <strong>⚠️ Important:</strong> Use this exact email on Ko-fi:
                                            </p>
                                            <div className="bg-white rounded-lg p-3 border border-amber-200">
                                                <p className="text-base font-bold text-slate-900 text-center break-all">
                                                    {userData?.email || "your billing email"}
                                                </p>
                                            </div>
                                            <p className="text-xs text-amber-700 mt-2 text-center">
                                                Copy this email and paste it into the Ko-fi payment form for instant activation
                                            </p>
                                        </div>

                                        <div className="flex flex-col gap-3 text-sm">
                                            <a
                                                href={KOFI_LINK}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-blue-600 hover:text-blue-700 font-medium underline"
                                            >
                                                Didn't open? Click here to complete payment
                                            </a>
                                            <button
                                                onClick={() => setIsWaitingForPayment(false)}
                                                className="text-slate-400 hover:text-slate-600 text-xs"
                                            >
                                                Go back to edit preferences
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}


                        {/* Step 3: Active - Show when user is premium (PRIORITY: isPremium overrides hasProfile) */}
                        {user && isPremium && (
                            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 p-8 text-center animate-fade-in">
                                <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center text-white mx-auto mb-4 shadow-xl shadow-green-500/30">
                                    <Activity className="w-8 h-8" />
                                </div>
                                <h2 className="text-2xl font-bold text-slate-900 mb-2">You're Active!</h2>
                                <p className="text-slate-500 mb-6">
                                    We are monitoring {clinicCount}+ clinics for you 24/7.
                                </p>

                                <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-slate-500">Status</span>
                                        <span className="font-bold text-green-600 flex items-center gap-1">
                                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                            Monitoring
                                        </span>
                                    </div>
                                </div>

                                <a
                                    href={KOFI_MANAGE_LINK}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="mt-6 text-sm text-blue-500 hover:text-blue-600 font-medium inline-flex items-center gap-1"
                                >
                                    Manage Subscription <Zap className="w-3 h-3" />
                                </a>
                            </div>
                        )}

                        {/* My Preferences Card - Show for all premium users */}
                        {user && isPremium && (
                            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 p-6 animate-fade-in">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="font-bold text-slate-900 flex items-center gap-2">
                                        <Settings className="w-5 h-5 text-slate-500" />
                                        My Preferences
                                    </h3>
                                    <button
                                        onClick={() => setShowPreferencesModal(true)}
                                        className="text-xs font-bold text-blue-600 hover:text-blue-700 bg-blue-50 px-3 py-1.5 rounded-full hover:bg-blue-100 transition-colors"
                                    >
                                        {hasProfile ? 'Edit Settings' : 'Set Preferences'}
                                    </button>
                                </div>

                                {hasProfile && userData ? (
                                    <div className="space-y-4">
                                        <div>
                                            <p className="text-xs font-bold text-slate-400 uppercase mb-2">Monitoring Area</p>
                                            <div className="flex flex-wrap gap-2">
                                                <span className="px-2 py-1 rounded-md bg-slate-100 text-slate-600 text-xs font-bold border border-slate-200">
                                                    {userData.province || "ON"}
                                                </span>
                                                {userData.areas && userData.areas.length > 0 ? (
                                                    userData.areas.map((area: string) => (
                                                        <span key={area} className="px-2 py-1 rounded-md bg-blue-50 text-blue-700 text-xs font-bold border border-blue-100 flex items-center gap-1">
                                                            <MapPin className="w-3 h-3" />
                                                            {area}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <span className="text-xs text-amber-600 font-medium italic">No areas selected</span>
                                                )}
                                            </div>
                                        </div>

                                        {userData.languages && userData.languages.length > 0 && (
                                            <div>
                                                <p className="text-xs font-bold text-slate-400 uppercase mb-2">Languages</p>
                                                <div className="flex flex-wrap gap-2">
                                                    {userData.languages.map((lang: string) => (
                                                        <span key={lang} className="px-2 py-1 rounded-md bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-100">
                                                            {lang}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="text-center py-6">
                                        <p className="text-sm text-slate-500 mb-3">
                                            Set your monitoring preferences to get started
                                        </p>
                                        <button
                                            onClick={() => setShowPreferencesModal(true)}
                                            className="text-sm font-bold text-blue-600 hover:text-blue-700 underline"
                                        >
                                            Configure Now →
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Trust Signals (Below Auth/Preferences) */}
                        <div className="grid grid-cols-2 gap-4">
                            <TrustCard
                                icon={Zap}
                                title="Instant SMS"
                                desc="Get alerted within seconds"
                            />
                            <TrustCard
                                icon={Activity}
                                title="24/7 Monitoring"
                                desc="Never miss an opening"
                            />
                        </div>
                    </div>

                    {/* RIGHT COLUMN: Proof Zone (Scrollable) */}
                    <div className="order-2 lg:col-span-7 space-y-6">

                        {/* Live Clinic List */}
                        <div className="bg-white/60 backdrop-blur-md rounded-3xl shadow-xl border border-white/50 p-6">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
                                    <div className="w-1.5 h-8 bg-blue-600 rounded-full" />
                                    Live Clinic Status
                                    <span className="relative flex h-3 w-3 ml-1">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                    </span>
                                </h2>
                                <div className="hidden md:flex items-center gap-2 text-xs font-medium text-slate-500">
                                    <Clock className="w-3 h-3" />
                                    Last checked {lastChecked ? getTimeAgo(lastChecked) : 'recently'}
                                </div>
                            </div>
                            <ClinicList paymentUrl={paymentUrl} isPremium={isPremium} onLastCheckedUpdate={setLastChecked} />
                        </div>
                    </div>
                </div>

                {/* Footer - Legal Disclaimers */}
                <footer className="mt-16 pt-8 border-t border-slate-200">
                    <div className="max-w-4xl mx-auto space-y-4">
                        <p className="text-xs text-center text-slate-500 leading-relaxed">
                            Clinic Scout is an independent technology service not affiliated with any government or medical body. All data is publicly available.
                        </p>
                        <div className="flex items-center justify-center gap-6 text-xs">
                            <Link href="/terms" className="text-slate-400 hover:text-slate-600 underline transition-colors">
                                Terms of Service
                            </Link>
                            <span className="text-slate-300">•</span>
                            <Link href="/privacy" className="text-slate-400 hover:text-slate-600 underline transition-colors">
                                Privacy Policy
                            </Link>
                        </div>
                        <p className="text-[10px] text-center text-slate-400">
                            © {new Date().getFullYear()} Clinic Scout. All rights reserved.
                        </p>
                    </div>
                </footer>
            </main>

            {/* Preferences Modal */}
            {showPreferencesModal && user && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
                    <div className="w-full max-w-lg relative">
                        <PreferencesForm user={user} mode="edit" onClose={() => setShowPreferencesModal(false)} />
                    </div>
                </div>
            )}
        </div>
    );
}

function TrustCard({ icon: Icon, title, desc }: { icon: any, title: string, desc: string }) {
    return (
        <div className="bg-white/50 backdrop-blur-sm border border-slate-200 p-5 rounded-2xl hover:bg-white transition-all hover:shadow-md">
            <Icon className="w-6 h-6 text-blue-600 mb-3" />
            <h3 className="font-bold text-slate-900 text-sm mb-1">{title}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">{desc}</p>
        </div>
    );
}
