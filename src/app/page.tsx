"use client";

import { useState, useEffect } from "react";
import { User } from "firebase/auth";
import { doc, getDoc, collection, getDocs, onSnapshot } from "firebase/firestore";
import { db, auth } from "@/lib/firebase";
import Auth from "@/components/Auth";
import ClinicList from "@/components/ClinicList";
import PreferencesForm from "@/components/PreferencesForm";
import { Zap, Activity, Settings, MapPin, Clock, Sparkles } from "lucide-react";

// Real Ko-fi membership tier direct link
const KOFI_LINK = "https://ko-fi.com/summary/2fa9d8df-c028-400e-bf9b-d3b065fab8cc";
const KOFI_MANAGE_LINK = "https://ko-fi.com/account/subscriptions";

export default function Home() {
    const [user, setUser] = useState<User | null>(null);
    const [isPremium, setIsPremium] = useState(false);
    const [hasProfile, setHasProfile] = useState(false);
    const [isWaitingForPayment, setIsWaitingForPayment] = useState(false);
    const [clinicCount, setClinicCount] = useState(0);
    const [showPreferencesModal, setShowPreferencesModal] = useState(false);
    const [userData, setUserData] = useState<any>(null);

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

    const paymentUrl = KOFI_LINK;

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
            {/* Sticky Header */}
            <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm">
                <div className="max-w-7xl mx-auto px-4 md:px-8 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-teal-600 rounded-xl flex items-center justify-center shadow-lg">
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

            <main className="max-w-7xl mx-auto px-4 md:px-8 py-8 md:py-12">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">

                    {/* LEFT COLUMN: Action Zone (Sticky) */}
                    <div className="lg:col-span-5 lg:sticky lg:top-28 space-y-8">

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
                                    Find a Family Doctor <span className="text-blue-600">Fast</span>
                                </h1>
                                <p className="text-lg text-slate-600 leading-relaxed">
                                    Stop refreshing websites. Our <span className="font-bold text-slate-900">AI agents</span> monitor 250+ clinics 24/7 and interpret waitlist status instantly, sending you an SMS the second a spot opens.
                                </p>
                            </div>
                        )}

                        {/* Step 1: Login (User is null) */}
                        {!user && (
                            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 overflow-hidden animate-fade-in">
                                <Auth onLogin={setUser} />
                            </div>
                        )}

                        {/* Step 2: Setup - Show PreferencesForm in embedded mode */}
                        {user && !hasProfile && !isWaitingForPayment && (
                            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 p-6 animate-fade-in">
                                <div className="mb-4">
                                    <h2 className="text-2xl font-bold text-slate-900 mb-2">Set Your Preferences</h2>
                                    <p className="text-sm text-slate-500">Tell us where to look for clinics</p>
                                </div>
                                <PreferencesForm
                                    user={user}
                                    mode="setup"
                                    onComplete={() => {
                                        // Auto-redirect to Ko-fi checkout
                                        setIsWaitingForPayment(true);
                                        window.open(KOFI_LINK, '_blank');
                                    }}
                                />
                            </div>
                        )}

                        {/* Listening for Payment - Show after preferences saved */}
                        {user && hasProfile && !isPremium && isWaitingForPayment && (
                            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 p-8 text-center animate-fade-in">
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

                                <div className="bg-amber-50 rounded-xl p-4 border border-amber-100 mb-6">
                                    <p className="text-xs text-amber-700">
                                        <strong>⚠️ Important:</strong> Use <span className="font-bold underline">{userData?.email || "your billing email"}</span> on Ko-fi to activate instantly.
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

                        {/* Step 4: Active - Show when user has profile AND is premium */}
                        {user && hasProfile && isPremium && (
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

                        {/* My Preferences Card - Only show if user is active (has profile and premium) */}
                        {user && hasProfile && isPremium && userData && (
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
                                        Edit Settings
                                    </button>
                                </div>

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
                    <div className="lg:col-span-7 space-y-6">

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
                                    Last checked 2m ago
                                </div>
                            </div>
                            <ClinicList paymentUrl={paymentUrl} isPremium={isPremium} />
                        </div>
                    </div>
                </div>
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
