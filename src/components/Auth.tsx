"use client";

import { useState, useEffect } from "react";
import { auth, db } from "@/lib/firebase";
import { signInAnonymously, onAuthStateChanged, User } from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";
import { ArrowRight } from "lucide-react";

export default function Auth({ onLogin }: { onLogin: (user: User) => void }) {
    const [phone, setPhone] = useState("");
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
            if (currentUser) {
                onLogin(currentUser);
            }
        });
        return () => unsubscribe();
    }, [onLogin]);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            // For demo/dev purposes, using anonymous auth + phone number storage
            // In production, use proper Phone Auth
            const userCredential = await signInAnonymously(auth);
            const user = userCredential.user;

            // Save phone number and email to profile
            await setDoc(doc(db, "users", user.uid), {
                phoneNumber: `+1${phone}`,
                email: email,
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
            <div className="text-center mb-8">
                <h1 className="text-3xl font-black text-slate-900 mb-2 tracking-tight">Get Instant Alerts</h1>
                <p className="text-slate-600 font-medium">Join 1,000+ locals tracking clinics.</p>
            </div>

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

                    <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-900 uppercase tracking-wider">Billing Email</label>
                        <div className="flex rounded-xl border border-slate-200 overflow-hidden focus-within:ring-4 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all shadow-sm bg-white">
                            <input
                                type="email"
                                required
                                placeholder="name@example.com"
                                className="flex-1 px-4 py-4 outline-none text-slate-900 font-bold text-lg placeholder:text-slate-300 bg-transparent"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <p className="text-[10px] text-slate-400">Used to verify your membership.</p>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={loading || phone.length !== 10 || !email.includes('@')}
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
    );
}
