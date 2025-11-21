"use client";

import { useState, useEffect } from "react";
import { doc, getDoc, setDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { User } from "firebase/auth";
import { Save, Loader2, X, Check, Mail, ShieldCheck } from "lucide-react";
import clsx from "clsx";

const PROVINCES = [
    { code: "ON", name: "Ontario" },
    { code: "BC", name: "British Columbia" },
    { code: "AB", name: "Alberta" },
];

const LOCATIONS: Record<string, string[]> = {
    "ON": ["Toronto", "Mississauga", "Brampton", "Markham", "Richmond Hill", "Vaughan", "Oakville", "Scarborough", "North York", "Etobicoke"],
    "BC": ["Vancouver", "Burnaby", "Richmond", "Surrey", "North Vancouver", "West Vancouver", "Coquitlam", "Delta"],
    "AB": ["Calgary", "Edmonton", "Red Deer", "Lethbridge"],
};

const LANGUAGES = ["English", "French", "Mandarin", "Cantonese", "Punjabi", "Hindi", "Spanish", "Arabic"];

// Email validation helper
const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

export default function PreferencesForm({ user, mode = 'setup', onClose, onComplete }: { user: User, mode?: 'setup' | 'edit', onClose?: () => void, onComplete?: (email: string) => void }) {
    const [province, setProvince] = useState("ON");
    const [selectedAreas, setSelectedAreas] = useState<string[]>([]);
    const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
    const [email, setEmail] = useState("");
    const [emailError, setEmailError] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [loading, setLoading] = useState(false);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        const fetchPreferences = async () => {
            if (!user) return;
            const docRef = doc(db, "users", user.uid);
            const docSnap = await getDoc(docRef);
            if (docSnap.exists()) {
                const data = docSnap.data();
                setProvince(data.province || "ON");
                setSelectedAreas(data.areas || []);
                setSelectedLanguages(data.languages || []);
                setEmail(data.email || "");
                setPhoneNumber(data.phoneNumber || "");
            }
        };
        fetchPreferences();
    }, [user]);

    const toggleArea = (area: string) => {
        setSelectedAreas(prev =>
            prev.includes(area) ? prev.filter(a => a !== area) : [...prev, area]
        );
    };

    const toggleLanguage = (lang: string) => {
        setSelectedLanguages(prev =>
            prev.includes(lang) ? prev.filter(l => l !== lang) : [...prev, lang]
        );
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();

        // Validate email
        if (!email || !isValidEmail(email)) {
            setEmailError('Please enter a valid email address');
            return;
        }

        setLoading(true);
        setSaved(false);
        setEmailError(''); // Clear any previous errors
        try {
            await setDoc(doc(db, "users", user.uid), {
                province,
                areas: selectedAreas,
                languages: selectedLanguages,
                email,
                updatedAt: new Date()
            }, { merge: true });
            setSaved(true);
            setTimeout(() => {
                setSaved(false);
                if (onClose) onClose();
                if (onComplete) onComplete(email); // Pass email to parent for Ko-fi redirect
            }, 1500);
        } catch (error) {
            console.error("Error saving preferences:", error);
            alert("Failed to save preferences.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSave} className={clsx(
            "bg-white p-6 rounded-2xl space-y-6 relative",
            mode === 'edit' ? "shadow-sm border border-slate-200" : ""
        )}>
            {onClose && (
                <button type="button" onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600">
                    <X className="w-5 h-5" />
                </button>
            )}

            <div>
                <h3 className="font-bold text-slate-900 text-lg">Your Preferences</h3>
                <p className="text-sm text-slate-500">Customize your alerts</p>
            </div>

            {/* Phone Number Input (Editable in setup mode, read-only in edit mode) */}
            <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                    Phone Number (Optional - for SMS alerts)
                </label>
                {mode === 'setup' ? (
                    <div className="relative">
                        <input
                            type="tel"
                            value={phoneNumber}
                            onChange={(e) => setPhoneNumber(e.target.value)}
                            placeholder="+1 (416) 555-1234"
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none font-medium text-slate-900 placeholder:text-slate-400 transition-all"
                        />
                        <p className="text-xs text-slate-400 mt-2">
                            Get instant SMS alerts when clinics open (optional)
                        </p>
                    </div>
                ) : (
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                                <ShieldCheck className="w-5 h-5 text-green-600" />
                            </div>
                            <div>
                                <p className="font-bold text-slate-900">{phoneNumber || "No phone linked"}</p>
                                <p className="text-xs text-green-600 font-bold flex items-center gap-1">
                                    <Check className="w-3 h-3" /> Verified
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Billing Email */}
            <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Billing Email <span className="text-red-500">*</span></label>
                <div className="relative">
                    <Mail className={clsx(
                        "absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5",
                        emailError ? "text-rose-400" : "text-slate-400"
                    )} />
                    <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => {
                            setEmail(e.target.value);
                            setEmailError(''); // Clear error as user types
                        }}
                        placeholder="your@email.com"
                        className={clsx(
                            "w-full pl-12 pr-4 py-3 rounded-xl border focus:ring-4 focus:ring-blue-500/20 outline-none font-medium text-slate-900 placeholder:text-slate-400 transition-all",
                            emailError
                                ? "border-rose-500 focus:border-rose-500"
                                : "border-slate-200 focus:border-blue-500"
                        )}
                    />
                </div>
                {emailError ? (
                    <p className="text-xs text-rose-600 mt-2 font-medium">{emailError}</p>
                ) : (
                    <p className="text-xs text-slate-400 mt-2">
                        Must match your payment email for instant activation
                    </p>
                )}
            </div>

            {/* Province Selector */}
            <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Province</label>
                <div className="flex gap-2">
                    {PROVINCES.map((p) => (
                        <button
                            key={p.code}
                            type="button"
                            onClick={() => {
                                setProvince(p.code);
                                setSelectedAreas([]); // Reset areas when province changes
                            }}
                            className={clsx(
                                "px-4 py-2 rounded-lg text-sm font-medium transition-all border",
                                province === p.code
                                    ? "bg-slate-900 text-white border-slate-900 shadow-md"
                                    : "bg-white text-slate-600 border-slate-200 hover:border-slate-300"
                            )}
                        >
                            {p.code}
                        </button>
                    ))}
                </div>
            </div>

            {/* Area Selector (Multi-select) */}
            <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                    Target Areas in {PROVINCES.find(p => p.code === province)?.name}
                </label>
                <div className="flex flex-wrap gap-2">
                    {LOCATIONS[province]?.map((area) => (
                        <button
                            key={area}
                            type="button"
                            onClick={() => toggleArea(area)}
                            className={clsx(
                                "px-3 py-1.5 rounded-full text-xs font-bold transition-all border flex items-center gap-1.5",
                                selectedAreas.includes(area)
                                    ? "bg-blue-50 text-blue-700 border-blue-200 shadow-sm"
                                    : "bg-slate-50 text-slate-500 border-slate-200 hover:bg-slate-100"
                            )}
                        >
                            {selectedAreas.includes(area) && <Check className="w-3 h-3" />}
                            {area}
                        </button>
                    ))}
                </div>
                {selectedAreas.length === 0 && (
                    <p className="text-xs text-amber-600 mt-2 font-medium">
                        * Select at least one area to receive relevant alerts.
                    </p>
                )}
            </div>

            {/* Language Selector */}
            <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Preferred Languages</label>
                <div className="flex flex-wrap gap-2">
                    {LANGUAGES.map((lang) => (
                        <button
                            key={lang}
                            type="button"
                            onClick={() => toggleLanguage(lang)}
                            className={clsx(
                                "px-3 py-1.5 rounded-full text-xs font-bold transition-all border",
                                selectedLanguages.includes(lang)
                                    ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                                    : "bg-slate-50 text-slate-500 border-slate-200 hover:bg-slate-100"
                            )}
                        >
                            {lang}
                        </button>
                    ))}
                </div>
            </div>

            {/* Legal Disclaimer - Clickwrap Notice */}
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                <strong>Disclaimer:</strong> By clicking below, you acknowledge that Clinic Scout is a technical notification service only. We do not guarantee appointments, provide medical advice, or offer preferential access to care.
            </div>

            <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2 disabled:opacity-50 hover:-translate-y-0.5"
            >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
                {saved ? "Preferences Saved!" : (mode === 'setup' ? "Save & Join on Ko-fi ($5/mo) →" : "Save Changes")}
            </button>
        </form>
    );
}
