import { useState, useEffect } from "react";
import { auth, db } from "@/lib/firebase";
import { signInAnonymously, onAuthStateChanged, User, sendSignInLinkToEmail } from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";
import { ArrowRight, Mail } from "lucide-react";
import clsx from "clsx";

export default function Auth({ onLogin }: { onLogin: (user: User) => void }) {
    const [phone, setPhone] = useState("");
    const [email, setEmail] = useState("");
    const [authMethod, setAuthMethod] = useState<"PHONE" | "EMAIL">("PHONE");
    const [emailSent, setEmailSent] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
            if (currentUser) {
                onLogin(currentUser);
            }
        });
        return () => unsubscribe();
    }, [onLogin]);

    const handleEmailLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            // Determine redirect URL
            let redirectUrl = window.location.href;
            if (window.location.hostname !== 'localhost' && !window.location.hostname.includes('127.0.0.1')) {
                redirectUrl = "https://www.clinicscout.ca/";
            }

            const actionCodeSettings = {
                url: redirectUrl,
                handleCodeInApp: true,
            };

            await sendSignInLinkToEmail(auth, email, actionCodeSettings);
            window.localStorage.setItem('emailForSignIn', email);
            setEmailSent(true);
        } catch (error: any) {
            console.error("Email login failed", error);
            alert(`Failed to send login link: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

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

            // onLogin will be called by onAuthStateChanged
        } catch (error: any) {
            console.error("Login failed", error);
            alert(`Login failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full p-8">
            <div className="flex justify-center gap-4 mb-8">
                <button
                    onClick={() => setAuthMethod("PHONE")}
                    className={clsx(
                        "px-6 py-2 rounded-full text-sm font-bold transition-all border",
                        authMethod === "PHONE"
                            ? "bg-blue-50 text-blue-600 border-blue-200 shadow-sm"
                            : "bg-white text-slate-400 border-slate-100 hover:border-slate-200"
                    )}
                >
                    📱 Phone
                </button>
                <button
                    onClick={() => setAuthMethod("EMAIL")}
                    className={clsx(
                        "px-6 py-2 rounded-full text-sm font-bold transition-all border",
                        authMethod === "EMAIL"
                            ? "bg-blue-50 text-blue-600 border-blue-200 shadow-sm"
                            : "bg-white text-slate-400 border-slate-100 hover:border-slate-200"
                    )}
                >
                    📧 Email
                </button>
            </div>

            <div className="text-center mb-8">
                <h1 className="text-3xl font-black text-slate-900 mb-2 tracking-tight">
                    {authMethod === "EMAIL" ? "Welcome Back" : "Get Instant Alerts"}
                </h1>
                <p className="text-slate-600 font-medium">
                    {authMethod === "EMAIL"
                        ? "Enter the email to restore your premium access"
                        : "Join 1,000+ locals tracking clinics."}
                </p>
            </div>

            {authMethod === "PHONE" ? (
                <form onSubmit={handleLogin} className="space-y-6 max-w-sm mx-auto">
                    <div className="space-y-4">
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
                    </div>

                    <button
                        type="submit"
                        disabled={loading || phone.length !== 10}
                        className="group relative w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-5 rounded-xl shadow-xl shadow-blue-600/20 transition-all hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 overflow-hidden animate-pulse hover:animate-none"
                    >
                        <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-shimmer" />
                        <span className="text-lg">{loading ? "Verifying..." : "Start Finding a Doctor →"}</span>
                        {!loading && <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />}
                    </button>

                    <p className="text-[10px] text-center text-slate-500 font-medium mt-2">
                        Join 1,000+ Canadians tracking clinics today.
                    </p>

                    <p className="text-[10px] text-center text-slate-400 leading-relaxed max-w-xs mx-auto mt-3">
                        By continuing, you agree to our Terms. This service tracks administrative availability only and does not provide medical care.
                    </p>
                </form>
            ) : (
                <form onSubmit={handleEmailLogin} className="space-y-6 max-w-sm mx-auto">
                    {emailSent ? (
                        <div className="bg-green-50 border border-green-100 rounded-xl p-6 text-center animate-fade-in">
                            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-green-600 mx-auto mb-3">
                                <Mail className="w-6 h-6" />
                            </div>
                            <h3 className="text-lg font-bold text-green-900 mb-2">Check your email!</h3>
                            <p className="text-sm text-green-700 mb-4">
                                We sent a magic login link to <strong>{email}</strong>.
                            </p>
                            <p className="text-xs text-green-600/80">
                                Click the link in the email to complete your login.
                            </p>
                        </div>
                    ) : (
                        <>
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-slate-900 uppercase tracking-wider">Email Address</label>
                                <div className="flex rounded-xl border border-slate-200 overflow-hidden focus-within:ring-4 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all shadow-sm bg-white">
                                    <div className="bg-slate-50 px-4 py-4 border-r border-slate-200 text-slate-500 font-medium flex items-center gap-2">
                                        <Mail className="w-5 h-5" />
                                    </div>
                                    <input
                                        type="email"
                                        required
                                        placeholder="user@example.com"
                                        className="flex-1 px-4 py-4 outline-none text-slate-900 font-bold text-lg placeholder:text-slate-300 bg-transparent"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading || !email}
                                className="group relative w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-5 rounded-xl shadow-xl shadow-blue-600/20 transition-all hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 overflow-hidden"
                            >
                                <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-shimmer" />
                                <span className="text-lg">{loading ? "Sending Link..." : "Log in to Dashboard"}</span>
                                {!loading && <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />}
                            </button>
                        </>
                    )}
                </form>
            )}
        </div>
    );
}
