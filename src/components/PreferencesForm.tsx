"use client";

import { useState, useEffect } from "react";
import { doc, getDoc, setDoc, collection, getDocs } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { User } from "firebase/auth";
import { Save, Loader2, X, Check, Mail, ShieldCheck } from "lucide-react";
import clsx from "clsx";

const PROVINCES = [
    { code: "ON", name: "Ontario" },
    { code: "BC", name: "British Columbia" },
    { code: "AB", name: "Alberta" },
];


// Hardcoded LOCATIONS removed - now fetched from Firebase
// const LOCATIONS: Record<string, string[]> = { ... };


// Hardcoded LANGUAGES removed - now fetched from Firebase
// const LANGUAGES = ["English", "French", "Mandarin", "Cantonese", "Punjabi", "Hindi", "Spanish", "Arabic"];

// Email validation helper
const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

// Phone number validation and formatting to E.164 format
const formatPhoneToE164 = (phone: string): string | null => {
    // Remove all non-digit characters
    const digits = phone.replace(/\D/g, '');

    // Check if it's a valid North American number (10 or 11 digits)
    if (digits.length === 10) {
        // Assume US/Canada, add +1
        return `+1${digits}`;
    } else if (digits.length === 11 && digits.startsWith('1')) {
        // Already has country code
        return `+${digits}`;
    } else if (phone.startsWith('+') && digits.length >= 10) {
        // Already in E.164 format
        return `+${digits}`;
    }

    return null; // Invalid format
};

const isValidPhone = (phone: string): boolean => {
    if (!phone) return true; // Optional field
    return formatPhoneToE164(phone) !== null;
};

export default function PreferencesForm({ user, mode = 'setup', onClose, onComplete }: { user: User, mode?: 'setup' | 'edit', onClose?: () => void, onComplete?: (email: string) => void }) {
    const [province, setProvince] = useState("ON");
    const [selectedAreas, setSelectedAreas] = useState<string[]>([]);
    const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
    const [email, setEmail] = useState("");
    const [emailError, setEmailError] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [phoneError, setPhoneError] = useState("");
    const [loading, setLoading] = useState(false);
    const [saved, setSaved] = useState(false);
    const [availableAreas, setAvailableAreas] = useState<Record<string, string[]>>({});
    const [loadingAreas, setLoadingAreas] = useState(true);
    const [availableLanguages, setAvailableLanguages] = useState<string[]>([]);
    const [loadingLanguages, setLoadingLanguages] = useState(true);
    const [showAllAreas, setShowAllAreas] = useState(false); // For compact mode on mobile

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

    // Fetch available areas from Firebase clinics collection
    useEffect(() => {
        const fetchAvailableAreas = async () => {
            setLoadingAreas(true);
            try {
                const clinicsRef = collection(db, "clinics");
                const clinicsSnap = await getDocs(clinicsRef);

                // Group unique districts by province
                const areasByProvince: Record<string, Set<string>> = {
                    "ON": new Set(),
                    "BC": new Set(),
                    "AB": new Set(),
                };

                clinicsSnap.forEach((doc) => {
                    const data = doc.data();
                    const district = data.district;
                    const province = data.province;

                    if (district && province && areasByProvince[province]) {
                        // Add district to the appropriate province
                        areasByProvince[province].add(district);
                    }
                });

                // Convert Sets to sorted arrays
                const areasObject: Record<string, string[]> = {};
                Object.keys(areasByProvince).forEach((prov) => {
                    areasObject[prov] = Array.from(areasByProvince[prov]).sort();
                });

                setAvailableAreas(areasObject);
            } catch (error) {
                console.error("Error fetching areas:", error);
                // Fallback to empty arrays if fetch fails
                setAvailableAreas({
                    "ON": [],
                    "BC": [],
                    "AB": [],
                });
            } finally {
                setLoadingAreas(false);
            }
        };

        fetchAvailableAreas();
    }, []);

    // Fetch available languages from Firebase clinics collection
    useEffect(() => {
        const fetchAvailableLanguages = async () => {
            setLoadingLanguages(true);
            try {
                const clinicsRef = collection(db, "clinics");
                const clinicsSnap = await getDocs(clinicsRef);

                // Collect unique languages
                const languagesSet = new Set<string>();

                clinicsSnap.forEach((doc) => {
                    const data = doc.data();
                    const languages = data.languages;

                    if (Array.isArray(languages)) {
                        languages.forEach((lang: string) => {
                            if (lang) languagesSet.add(lang);
                        });
                    }
                });

                // Convert Set to sorted array
                const languagesArray = Array.from(languagesSet).sort();
                setAvailableLanguages(languagesArray);
            } catch (error) {
                console.error("Error fetching languages:", error);
                // Fallback to empty array if fetch fails
                setAvailableLanguages([]);
            } finally {
                setLoadingLanguages(false);
            }
        };

        fetchAvailableLanguages();
    }, []);

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

        // Validate areas - must select at least one
        if (selectedAreas.length === 0) {
            alert('Please select at least one area to receive alerts.');
            return;
        }

        // Validate and format phone number to E.164
        let formattedPhone = '';
        if (phoneNumber) {
            const e164Phone = formatPhoneToE164(phoneNumber);
            if (!e164Phone) {
                setPhoneError('Please enter a valid phone number (e.g., +1 416 555 1234)');
                return;
            }
            formattedPhone = e164Phone;
        }

        setLoading(true);
        setSaved(false);
        setEmailError(''); // Clear any previous errors
        setPhoneError(''); // Clear any previous errors
        try {
            // Use merge: true to update without overwriting other fields (like isPremium)
            await setDoc(doc(db, "users", user.uid), {
                province,
                areas: selectedAreas,
                languages: selectedLanguages,
                email,
                phoneNumber: formattedPhone,  // Save in E.164 format
                updatedAt: new Date()
            }, { merge: true });

            setSaved(true);

            // Different UX for edit vs setup mode
            if (mode === 'edit') {
                // Edit mode: Show success message and close
                alert('Settings updated successfully!');
                setTimeout(() => {
                    setSaved(false);
                    if (onClose) onClose();
                    // In edit mode, don't pass email to onComplete
                    if (onComplete) onComplete('');
                }, 500);
            } else {
                // Setup mode: Pass email for Ko-fi redirect
                setTimeout(() => {
                    setSaved(false);
                    if (onClose) onClose();
                    if (onComplete) onComplete(email);
                }, 1500);
            }
        } catch (error) {
            console.error("Error saving preferences:", error);
            alert("Failed to save preferences. Please try again.");
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

            {/* Scrollable Content Wrapper for Mobile */}
            <div className="max-h-[60vh] overflow-y-auto scrollbar-thin px-1 space-y-4 md:space-y-6">
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
                                onChange={(e) => {
                                    setPhoneNumber(e.target.value);
                                    setPhoneError(''); // Clear error as user types
                                }}
                                placeholder="+1 (416) 555-1234"
                                className={clsx(
                                    "w-full px-4 py-3 rounded-xl border focus:ring-4 focus:ring-blue-500/20 outline-none font-medium text-slate-900 placeholder:text-slate-400 transition-all",
                                    phoneError
                                        ? "border-rose-500 focus:border-rose-500"
                                        : "border-slate-200 focus:border-blue-500"
                                )}
                            />
                            {phoneError ? (
                                <p className="text-xs text-rose-600 mt-2 font-medium">{phoneError}</p>
                            ) : (
                                <p className="text-xs text-slate-400 mt-2">
                                    Get instant SMS alerts when clinics open (optional)
                                </p>
                            )}
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

                    {/* Mobile: Dropdown */}
                    <select
                        value={province}
                        onChange={(e) => {
                            setProvince(e.target.value);
                            setSelectedAreas([]); // Reset areas when province changes
                            setShowAllAreas(false); // Reset compact mode
                        }}
                        className="md:hidden w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 outline-none font-medium text-slate-900 bg-white"
                    >
                        {PROVINCES.map((p) => (
                            <option key={p.code} value={p.code}>
                                {p.name}
                            </option>
                        ))}
                    </select>

                    {/* Desktop: Button Group */}
                    <div className="hidden md:flex gap-2">
                        {PROVINCES.map((p) => (
                            <button
                                key={p.code}
                                type="button"
                                onClick={() => {
                                    setProvince(p.code);
                                    setSelectedAreas([]); // Reset areas when province changes
                                    setShowAllAreas(false); // Reset compact mode
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

                {/* Area Selector with Compact Mode */}
                <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                        Target Areas in {PROVINCES.find(p => p.code === province)?.name}
                        {selectedAreas.length > 0 && ` (${selectedAreas.length} selected)`}
                    </label>
                    {loadingAreas ? (
                        <div className="flex items-center justify-center py-8">
                            <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                            <span className="ml-2 text-sm text-slate-500">Loading areas...</span>
                        </div>
                    ) : availableAreas[province]?.length > 0 ? (
                        <div className="space-y-3">
                            <div className="flex flex-wrap gap-2">
                                {(showAllAreas
                                    ? availableAreas[province]
                                    : availableAreas[province].slice(0, 6)
                                ).map((area) => (
                                    <button
                                        key={area}
                                        type="button"
                                        onClick={() => toggleArea(area)}
                                        className={clsx(
                                            "px-3 py-1.5 rounded-full text-xs font-bold transition-all border",
                                            selectedAreas.includes(area)
                                                ? "bg-blue-50 text-blue-700 border-blue-200"
                                                : "bg-slate-50 text-slate-500 border-slate-200 hover:bg-slate-100"
                                        )}
                                    >
                                        {area}
                                    </button>
                                ))}
                            </div>

                            {/* Show More/Less Toggle */}
                            {availableAreas[province].length > 6 && (
                                <button
                                    type="button"
                                    onClick={() => setShowAllAreas(!showAllAreas)}
                                    className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors flex items-center gap-1"
                                >
                                    {showAllAreas
                                        ? "− Show Less"
                                        : `+ Show All (${availableAreas[province].length})`
                                    }
                                </button>
                            )}
                        </div>
                    ) : (
                        <p className="text-sm text-slate-500 py-4">
                            No areas available for {PROVINCES.find(p => p.code === province)?.name} yet.
                        </p>
                    )}
                    {selectedAreas.length === 0 && (
                        <p className="text-xs text-amber-600 mt-2 font-medium">
                            * Select at least one area to receive relevant alerts.
                        </p>
                    )}
                </div>

                {/* Language Selector */}
                <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Preferred Languages</label>
                    {loadingLanguages ? (
                        <div className="flex items-center justify-center py-8">
                            <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                            <span className="ml-2 text-sm text-slate-500">Loading languages...</span>
                        </div>
                    ) : availableLanguages.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {availableLanguages.map((lang) => (
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
                    ) : (
                        <p className="text-sm text-slate-500 py-4">
                            No languages available yet.
                        </p>
                    )}
                </div>
            </div>
            {/* End Scrollable Content */}

            {/* Sticky Footer */}
            <div className="pt-4 border-t border-slate-100 mt-4 space-y-4">
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
            </div>
            {/* End Sticky Footer */}
        </form>
    );
}
