"use client";

import { useEffect, useState } from "react";
import { collection, onSnapshot, query, orderBy, doc, updateDoc, increment } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { MapPin, Phone, Search, Clock, CheckCircle2, XCircle, AlertCircle, Filter, ThumbsUp, ThumbsDown, Loader2, Lock } from "lucide-react";
import clsx from "clsx";

interface Clinic {
    id: string;
    name: string;
    status: "OPEN" | "CLOSED" | "WAITLIST" | "UNCERTAIN" | "ERROR";
    district: string;
    address: string;
    phone: string;
    url: string;
    updatedAt: any;
    success_count?: number;
    failure_count?: number;
    languages?: string[];
}

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

export default function ClinicList({ paymentUrl, isPremium = false }: { paymentUrl: string, isPremium?: boolean }) {
    const [clinics, setClinics] = useState<Clinic[]>([]);
    const [filteredClinics, setFilteredClinics] = useState<Clinic[]>([]);
    const [loading, setLoading] = useState(true);
    const [filterStatus, setFilterStatus] = useState<"ALL" | "OPEN" | "WAITLIST">("ALL");
    const [selectedProvince, setSelectedProvince] = useState("ALL");
    const [locationFilter, setLocationFilter] = useState("ALL");
    const [selectedLanguage, setSelectedLanguage] = useState("ALL");
    const [userVotes, setUserVotes] = useState<Record<string, 'success' | 'failure'>>({});

    useEffect(() => {
        const storedVotes = localStorage.getItem("clinic_votes");
        if (storedVotes) {
            try {
                setUserVotes(JSON.parse(storedVotes));
            } catch (e) {
                console.error("Failed to parse stored votes", e);
            }
        }
    }, []);

    useEffect(() => {
        const q = query(collection(db, "clinics"), orderBy("updatedAt", "desc"));

        // Set a timeout to prevent infinite loading
        const timeoutId = setTimeout(() => {
            setLoading((currentLoading) => {
                if (currentLoading) {
                    console.error("Firebase connection timed out");
                    return false;
                }
                return currentLoading;
            });
        }, 8000);

        const unsubscribe = onSnapshot(q, (snapshot) => {
            clearTimeout(timeoutId);
            const clinicData = snapshot.docs.map((doc) => {
                const data = doc.data();
                let languages = data.languages;

                // Default to English if missing, empty, or "N/A"
                if (!languages || languages === "N/A" || (Array.isArray(languages) && languages.length === 0)) {
                    languages = ["English"];
                } else if (typeof languages === 'string') {
                    // Handle case where it might be a comma-separated string
                    languages = languages.split(',').map(l => l.trim());
                }

                return {
                    id: doc.id,
                    ...data,
                    languages,
                };
            }) as Clinic[];

            // Filter out ERROR and UNCERTAIN
            const validClinics = clinicData.filter(c => c.status !== "ERROR" && c.status !== "UNCERTAIN");

            setClinics(validClinics);
            setLoading(false);
        }, (error) => {
            clearTimeout(timeoutId);
            console.error("Error fetching clinics:", error);
            setLoading(false);
        });
        return () => {
            unsubscribe();
            clearTimeout(timeoutId);
        };
    }, []);

    useEffect(() => {
        let result = [...clinics];

        // Filter by Status
        if (filterStatus !== "ALL") {
            result = result.filter(c => c.status === filterStatus);
        }

        // Filter by Province
        if (selectedProvince !== "ALL") {
            const provinceLocations = LOCATIONS[selectedProvince] || [];
            // Check if clinic's district/city matches any in the province list
            // Or if we have a province field (assuming we might not, so we use the list)
            result = result.filter(c => provinceLocations.some(loc => c.district.includes(loc)));
        }

        // Filter by Location
        if (locationFilter !== "ALL") {
            result = result.filter(c => c.district.includes(locationFilter));
        }

        // Filter by Language
        if (selectedLanguage !== "ALL") {
            result = result.filter(c => c.languages?.includes(selectedLanguage));
        }

        // Sorting Logic: Status Priority -> Social Proof (Net Score)
        result.sort((a, b) => {
            // 1. Status Priority: OPEN > WAITLIST > CLOSED
            const statusOrder: Record<string, number> = { OPEN: 0, WAITLIST: 1, CLOSED: 2 };
            const statusA = statusOrder[a.status] ?? 99;
            const statusB = statusOrder[b.status] ?? 99;

            if (statusA !== statusB) {
                return statusA - statusB;
            }

            // 2. Social Proof: Higher Net Score (Success - Failure) first
            const scoreA = (a.success_count || 0) - (a.failure_count || 0);
            const scoreB = (b.success_count || 0) - (b.failure_count || 0);
            return scoreB - scoreA;
        });

        setFilteredClinics(result);
    }, [clinics, filterStatus, selectedProvince, locationFilter]);

    const handleVote = async (clinicId: string, type: 'success' | 'failure') => {
        if (userVotes[clinicId]) return; // Prevent duplicate voting

        // Optimistic update
        const newVotes = { ...userVotes, [clinicId]: type };
        setUserVotes(newVotes);
        localStorage.setItem("clinic_votes", JSON.stringify(newVotes));

        try {
            const ref = doc(db, "clinics", clinicId);
            await updateDoc(ref, {
                [type === 'success' ? 'success_count' : 'failure_count']: increment(1)
            });
        } catch (error) {
            console.error("Error voting:", error);
            // Revert on error (optional, but good practice)
            const revertedVotes = { ...newVotes };
            delete revertedVotes[clinicId];
            setUserVotes(revertedVotes);
            localStorage.setItem("clinic_votes", JSON.stringify(revertedVotes));
            alert("Failed to register vote. Please try again.");
        }
    };

    if (loading) {
        return <div className="text-center py-20 text-slate-400 animate-pulse">Loading live data...</div>;
    }

    // Paywall Logic
    const visibleCount = isPremium ? filteredClinics.length : 3;
    const blurredCount = isPremium ? 0 : 6; // Show 6 blurred cards
    const visibleClinics = filteredClinics.slice(0, visibleCount);
    const blurredClinics = filteredClinics.slice(visibleCount, visibleCount + blurredCount);

    return (
        <div className="space-y-6 relative">
            {/* Controls */}
            <div className="flex flex-col md:flex-row gap-4 justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-slate-200">

                {/* Filters Group */}
                <div className="flex flex-wrap gap-3 w-full xl:w-auto flex-1">

                    {/* Province Filter */}
                    <select
                        value={selectedProvince}
                        onChange={(e) => {
                            setSelectedProvince(e.target.value);
                            setLocationFilter("ALL"); // Reset location when province changes
                        }}
                        className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm font-medium text-slate-600"
                    >
                        <option value="ALL">All Provinces</option>
                        {PROVINCES.map(p => (
                            <option key={p.code} value={p.code}>{p.name}</option>
                        ))}
                    </select>

                    {/* Location Filter */}
                    <select
                        value={locationFilter}
                        onChange={(e) => setLocationFilter(e.target.value)}
                        disabled={selectedProvince === "ALL"}
                        className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm font-medium text-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <option value="ALL">All Locations</option>
                        {selectedProvince !== "ALL" && LOCATIONS[selectedProvince]?.map(location => (
                            <option key={location} value={location}>{location}</option>
                        ))}
                    </select>

                    {/* Language Filter */}
                    <select
                        value={selectedLanguage}
                        onChange={(e) => setSelectedLanguage(e.target.value)}
                        className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm font-medium text-slate-600"
                    >
                        <option value="ALL">All Languages</option>
                        {LANGUAGES.map(lang => (
                            <option key={lang} value={lang}>{lang}</option>
                        ))}
                    </select>
                </div>

                {/* Status Filter Tabs */}
                <div className="flex p-1 bg-slate-100 rounded-xl shrink-0">
                    {(["ALL", "OPEN", "WAITLIST"] as const).map((status) => (
                        <button
                            key={status}
                            onClick={() => setFilterStatus(status)}
                            className={clsx(
                                "px-4 py-1.5 text-sm font-medium rounded-lg transition-all",
                                filterStatus === status
                                    ? "bg-white text-blue-700 shadow-sm"
                                    : "text-slate-500 hover:text-slate-700"
                            )}
                        >
                            {status === "ALL" ? "All" : status === "OPEN" ? "Open" : "Waitlist"}
                        </button>
                    ))}
                </div>
            </div>

            {/* List */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 relative">
                {filteredClinics.length > 0 ? (
                    <>
                        {/* Visible Clinics */}
                        {visibleClinics.map((clinic) => (
                            <ClinicCard
                                key={clinic.id}
                                clinic={clinic}
                                userVote={userVotes[clinic.id]}
                                onVote={(type) => handleVote(clinic.id, type)}
                            />
                        ))}

                        {/* Blurred Clinics (Visual Paywall) */}
                        {!isPremium && blurredClinics.map((clinic) => (
                            <div key={clinic.id} className="blur-sm pointer-events-none select-none opacity-60 grayscale">
                                <ClinicCard
                                    clinic={clinic}
                                    userVote={userVotes[clinic.id]}
                                    onVote={(type) => handleVote(clinic.id, type)}
                                />
                            </div>
                        ))}
                    </>
                ) : (
                    <div className="col-span-full text-center py-20 text-slate-500">
                        <Filter className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                        <p>No clinics found matching your filters.</p>
                    </div>
                )}

                {/* Paywall Overlay */}
                {!isPremium && filteredClinics.length > 3 && (
                    <div className="absolute inset-x-0 bottom-0 h-[400px] bg-gradient-to-t from-slate-50 via-slate-50/95 to-transparent z-20 flex flex-col items-center justify-end pb-20">
                        <div className="text-center p-6 max-w-md mx-auto animate-fade-in-up">
                            <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center text-white mx-auto mb-4 shadow-xl shadow-blue-600/20 rotate-3 hover:rotate-6 transition-transform">
                                <Lock className="w-8 h-8" />
                            </div>
                            <h3 className="text-2xl font-bold text-slate-900 mb-2">
                                {filteredClinics.length - 3 > 0
                                    ? `Unlock ${filteredClinics.length - 3}+ More Clinics + Instant SMS Alerts`
                                    : "Get Instant SMS Alerts When Spots Open"
                                }
                            </h3>
                            <p className="text-slate-500 mb-8">
                                Premium members see the full real-time list AND get instant text messages the second a spot opens.
                            </p>
                            <a
                                href={paymentUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-blue-700 transition-all shadow-xl shadow-blue-600/30 hover:-translate-y-1"
                            >
                                Upgrade for $5 / mo
                                <CheckCircle2 className="w-5 h-5" />
                            </a>
                            <p className="text-xs text-slate-400 mt-4">
                                One-time payment. Cancel anytime.
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function ClinicCard({ clinic, userVote, onVote }: { clinic: Clinic, userVote?: 'success' | 'failure', onVote: (type: 'success' | 'failure') => void }) {
    const [voting, setVoting] = useState(false);
    const handleVoteClick = async (type: 'success' | 'failure') => {
        if (voting || userVote) return;
        setVoting(true);
        await onVote(type);
        setVoting(false);
    };

    return (
        <div className="group bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md hover:border-blue-200 transition-all duration-200 flex flex-col h-full">
            <div className="flex justify-between items-start mb-3">
                <div className="flex-1 pr-2">
                    <h3 className="font-bold text-slate-900 leading-tight mb-1 group-hover:text-blue-700 transition-colors">
                        <a href={clinic.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                            {clinic.name}
                        </a>
                    </h3>
                </div>
                <StatusBadge status={clinic.status} />
            </div>

            <div className="space-y-2 text-sm text-slate-600 mt-4 pt-4 border-t border-slate-50 flex-grow">
                <div className="flex items-start gap-2">
                    <MapPin className="w-4 h-4 mt-0.5 text-slate-400 shrink-0" />
                    <span className="line-clamp-1">{clinic.address}, {clinic.district}</span>
                </div>
                {clinic.phone && clinic.phone !== "N/A" && clinic.phone !== "Unknown" && (
                    <div className="flex items-center gap-2">
                        <Phone className="w-4 h-4 text-slate-400 shrink-0" />
                        <span>{clinic.phone}</span>
                    </div>
                )}
            </div>

            {/* Social Proof / Voting Section */}
            <div className="mt-4 pt-3 border-t border-slate-50 flex gap-2">
                <button
                    onClick={() => handleVoteClick('success')}
                    disabled={voting || !!userVote}
                    className={clsx(
                        "flex-1 flex items-center justify-center gap-2 py-2 rounded-full text-xs font-bold transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
                        userVote === 'success'
                            ? "bg-teal-100 text-teal-700 ring-2 ring-teal-500 ring-offset-1"
                            : "bg-slate-100 hover:bg-teal-100 text-slate-600 hover:text-teal-700"
                    )}
                    title="I got an appointment!"
                >
                    {voting && !userVote ? <Loader2 className="w-3 h-3 animate-spin" /> : <ThumbsUp className={clsx("w-3.5 h-3.5", userVote === 'success' && "fill-current")} />}
                    <span>{clinic.success_count || 0}</span>
                </button>
                <button
                    onClick={() => handleVoteClick('failure')}
                    disabled={voting || !!userVote}
                    className={clsx(
                        "flex-1 flex items-center justify-center gap-2 py-2 rounded-full text-xs font-bold transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
                        userVote === 'failure'
                            ? "bg-rose-100 text-rose-700 ring-2 ring-rose-500 ring-offset-1"
                            : "bg-slate-100 hover:bg-rose-100 text-slate-600 hover:text-rose-700"
                    )}
                    title="Couldn't get in"
                >
                    {voting && !userVote ? <Loader2 className="w-3 h-3 animate-spin" /> : <ThumbsDown className={clsx("w-3.5 h-3.5", userVote === 'failure' && "fill-current")} />}
                    <span>{clinic.failure_count || 0}</span>
                </button>
            </div>
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    const styles = {
        OPEN: "bg-teal-50 text-teal-700 border-teal-200 ring-teal-500/20",
        CLOSED: "bg-rose-50 text-rose-600 border-rose-200 ring-rose-500/20",
        WAITLIST: "bg-yellow-50 text-yellow-700 border-yellow-100 ring-yellow-500/20",
        UNCERTAIN: "bg-slate-50 text-slate-600 border-slate-200 ring-slate-500/20",
    };

    const icons = {
        OPEN: CheckCircle2,
        CLOSED: XCircle,
        WAITLIST: AlertCircle,
        UNCERTAIN: AlertCircle,
    };

    const Icon = icons[status as keyof typeof icons] || AlertCircle;
    const style = styles[status as keyof typeof styles] || styles.UNCERTAIN;

    return (
        <span
            className={clsx(
                "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ring-1 ring-inset",
                style
            )}
        >
            <Icon className="w-3.5 h-3.5" />
            {status}
        </span>
    );
}
