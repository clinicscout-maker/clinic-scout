"use client";

import { useState, useEffect } from "react";
import { auth, db } from "@/lib/firebase";
import { signInAnonymously, onAuthStateChanged, User } from "firebase/auth";
import { doc, setDoc, getDoc } from "firebase/firestore";
import { Phone, ArrowRight, ShieldCheck, Coffee, ExternalLink } from "lucide-react";
import clsx from "clsx";

export default function Auth({ onLogin, paymentUrl, isPremium = false }: { onLogin: (user: User) => void, paymentUrl: string, isPremium?: boolean }) {
    const [phone, setPhone] = useState("");
    const [step, setStep] = useState<"LOGIN" | "MEMBERSHIP" | "ACTIVE">("LOGIN");
    const [loading, setLoading] = useState(false);
    const [user, setUser] = useState<User | null>(null);
    const [isWaitingForPayment, setIsWaitingForPayment] = useState(false);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
            if (currentUser) {
                setUser(currentUser);
                if (step === "LOGIN") {
                    setStep("MEMBERSHIP");
                }
                onLogin(currentUser);
            }
        });
        return () => unsubscribe();
    }, [onLogin, step]);

    // Watch for premium status update from parent (page.tsx)
    useEffect(() => {
        if (isPremium && step === "MEMBERSHIP") {
            setStep("ACTIVE");
            setIsWaitingForPayment(false);
        }
    }, [isPremium, step]);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            // For demo/dev purposes, using anonymous auth + phone number storage
            // In production, use proper Phone Auth
            const userCredential = await signInAnonymously(auth);
            const user = userCredential.user;

            // Save phone number to profile
            await setDoc(doc(db, "users", user.uid), {
                phoneNumber: `+1${phone}`,
                createdAt: new Date(),
            }, { merge: true });

            // Step transition handled by useEffect
        } catch (error: any) {
            console.error("Login failed", error);
            alert(`Login failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleMembershipClick = () => {
        setIsWaitingForPayment(true);
    };

    const handleManualCheck = async () => {
        if (!user) return;
        setLoading(true);
        try {
            const docRef = doc(db, "users", user.uid);
            const docSnap = await getDoc(docRef);
            if (docSnap.exists() && docSnap.data().isPremium) {
                setStep("ACTIVE");
                setIsWaitingForPayment(false);
            } else {
                alert("Payment not found yet. It usually takes 10-30 seconds.");
            }
        } catch (error) {
            console.error("Error checking payment:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full">
            {/* Stepper */}
            <div className="flex items-center justify-between px-8 py-6 border-b border-slate-100">
                <StepIndicator number={1} active={step === "LOGIN"} completed={step !== "LOGIN"} label="Login" />
                <div className={clsx("h-0.5 flex-1 mx-4", step !== "LOGIN" ? "bg-slate-900" : "bg-slate-100")} />
                <StepIndicator number={2} active={step === "MEMBERSHIP"} completed={step === "ACTIVE"} label="Membership" />
                <div className={clsx("h-0.5 flex-1 mx-4", step === "ACTIVE" ? "bg-slate-900" : "bg-slate-100")} />
                <StepIndicator number={3} active={step === "ACTIVE"} completed={false} label="Active" />
            </div>

            {/* Content */}
            <div className="p-8">
                {step === "LOGIN" && (
                    <div className="animate-fade-in">
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-black text-slate-900 mb-2 tracking-tight">Get Instant Alerts</h1>
                            <p className="text-slate-600 font-medium">Join 1,000+ locals tracking clinics.</p>
                        </div>

                        <form onSubmit={handleLogin} className="space-y-6 max-w-sm mx-auto">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-slate-900 uppercase tracking-wider">Mobile Number</label>
                                <div className="flex rounded-xl border border-slate-200 overflow-hidden focus-within:ring-4 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all shadow-sm bg-white">
                                    <div className="bg-slate-50 px-4 py-4 border-r border-slate-200 text-slate-500 font-medium flex items-center gap-2">
                                        <span>🇨🇦</span> +1
                                    </div>
                                    <input
                                        type="tel"
                                        required
                                        pattern="[0-9]{10}"
                                        placeholder="555 123 4567"
                                        className="flex-1 px-4 py-4 outline-none text-slate-900 font-bold text-lg placeholder:text-slate-300 bg-transparent"
                                        value={phone}
                                        onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading || phone.length !== 10}
                                className="group relative w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-5 rounded-xl shadow-xl shadow-blue-600/20 transition-all hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 overflow-hidden"
                            >
                                <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-shimmer" />
                                <span className="text-lg">{loading ? "Verifying..." : "Continue"}</span>
                                {!loading && <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />}
                            </button>

                            <p className="text-[10px] text-center text-slate-400 leading-relaxed max-w-xs mx-auto">
                                By continuing, you agree to receive SMS updates about clinic availability. Standard message and data rates may apply. Reply STOP to opt out.
                            </p>
                        </form>
                    </div>
                )}

                {step === "MEMBERSHIP" && (
                    <div className="text-center animate-fade-in max-w-sm mx-auto">
                        <div className="w-16 h-16 bg-[#FF5E5B] rounded-full flex items-center justify-center text-white mx-auto mb-6 shadow-xl shadow-[#FF5E5B]/30">
                            <Coffee className="w-8 h-8" />
                        </div>
                        <h2 className="text-2xl font-bold text-slate-900 mb-3">Join the Club</h2>
                        <p className="text-slate-500 mb-8">
                            Support our scouts and unlock instant SMS alerts for every clinic in your area.
                        </p>

                        <a
                            href={paymentUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={handleMembershipClick}
                            className="block w-full bg-[#FF5E5B] hover:bg-[#ff4643] text-white font-bold py-4 rounded-xl shadow-xl shadow-[#FF5E5B]/20 transition-all hover:-translate-y-0.5 mb-4 flex items-center justify-center gap-2"
                        >
                            Join Membership on Ko-fi
                            <ExternalLink className="w-4 h-4" />
                        </a>

                        {isWaitingForPayment && (
                            <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 mb-6 animate-fade-in">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="relative flex h-3 w-3">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
                                    </span>
                                    <p className="text-sm font-bold text-blue-900">Listening for payment confirmation...</p>
                                </div>
                                <p className="text-xs text-blue-700 mb-3 leading-relaxed">
                                    This usually takes 10-30 seconds after you complete payment on Ko-fi.
                                </p>
                                <button
                                    onClick={handleManualCheck}
                                    disabled={loading}
                                    className="w-full bg-white border border-blue-200 text-blue-700 text-xs font-bold py-2 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50"
                                >
                                    {loading ? "Checking..." : "I've Paid (Check Now)"}
                                </button>
                            </div>
                        )}

                        <p className="text-xs text-slate-400 bg-slate-50 p-3 rounded-lg border border-slate-100">
                            <strong>Important:</strong> Please use the SAME phone number as your login so we can link your account automatically.
                        </p>

                        <button onClick={() => setStep("ACTIVE")} className="mt-6 text-sm text-slate-400 hover:text-slate-600 underline">
                            I'm already a member
                        </button>
                    </div>
                )}

                {step === "ACTIVE" && (
                    <div className="text-center animate-fade-in py-4">
                        <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center text-white mx-auto mb-4 shadow-xl shadow-green-500/30">
                            <ShieldCheck className="w-8 h-8" />
                        </div>
                        <h2 className="text-2xl font-bold text-slate-900 mb-2">You're Active!</h2>
                        <p className="text-slate-500 mb-6">
                            We are monitoring clinics for you 24/7.
                        </p>

                        <div className="bg-slate-50 rounded-xl p-4 mb-6 border border-slate-100">
                            <div className="flex justify-between items-center text-sm mb-2">
                                <span className="text-slate-500">Status</span>
                                <span className="font-bold text-green-600 flex items-center gap-1">
                                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                    Monitoring
                                </span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-slate-500">Phone</span>
                                <span className="font-medium text-slate-900">+1 {phone}</span>
                            </div>
                        </div>

                        <a
                            href="https://ko-fi.com/account/subscriptions"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-500 hover:text-blue-600 font-medium flex items-center justify-center gap-1"
                        >
                            Manage Subscription <ExternalLink className="w-3 h-3" />
                        </a>
                    </div>
                )}
            </div>
        </div>
    );
}

function StepIndicator({ number, active, completed, label }: { number: number, active: boolean, completed: boolean, label: string }) {
    return (
        <div className="flex flex-col items-center gap-2 relative">
            <div className={clsx(
                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300",
                active ? "bg-slate-900 text-white scale-110 shadow-lg shadow-slate-900/20" :
                    completed ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-400"
            )}>
                {completed ? "✓" : number}
            </div>
            <span className={clsx(
                "text-[10px] font-bold uppercase tracking-wider absolute -bottom-5 whitespace-nowrap transition-colors",
                active ? "text-slate-900" : "text-slate-300"
            )}>
                {label}
            </span>
        </div>
    );
}
