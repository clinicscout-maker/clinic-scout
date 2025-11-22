export const PRIORITY_LANGUAGES = ["English", "French", "Cantonese", "Mandarin", "Japanese", "Korean"];

export function normalizeLanguage(lang: string): string {
    if (!lang) return "";
    // Simple Title Case: "ENGLISH" -> "English"
    const normalized = lang.charAt(0).toUpperCase() + lang.slice(1).toLowerCase();

    // Group translation services and 130+ languages
    const lower = normalized.toLowerCase();
    if (
        lower.includes("translation") ||
        lower.includes("interpreter") ||
        lower.includes("130") // Catch "130+", "130 +", "130 + langages"
    ) {
        return "Translation Services";
    }

    return normalized;
}

export function sortLanguages(languages: string[]): string[] {
    return languages.sort((a, b) => {
        const indexA = PRIORITY_LANGUAGES.indexOf(a);
        const indexB = PRIORITY_LANGUAGES.indexOf(b);

        // If both are priority, sort by priority order
        if (indexA !== -1 && indexB !== -1) return indexA - indexB;
        // If only A is priority, A comes first
        if (indexA !== -1) return -1;
        // If only B is priority, B comes first
        if (indexB !== -1) return 1;
        // Otherwise sort alphabetically
        return a.localeCompare(b);
    });
}

export const PRIORITY_AREAS_ON = [
    "Downtown Toronto",
    "Midtown Toronto",
    "North York",
    "Markham",
    "Richmond Hill",
    "Vaughan"
];

export function sortAreas(areas: string[], province: string): string[] {
    // Only apply custom sort for Ontario for now
    if (province !== "ON") {
        return areas.sort();
    }

    return areas.sort((a, b) => {
        const indexA = PRIORITY_AREAS_ON.indexOf(a);
        const indexB = PRIORITY_AREAS_ON.indexOf(b);

        // If both are priority, sort by priority order
        if (indexA !== -1 && indexB !== -1) return indexA - indexB;
        // If only A is priority, A comes first
        if (indexA !== -1) return -1;
        // If only B is priority, B comes first
        if (indexB !== -1) return 1;
        // Otherwise sort alphabetically
        return a.localeCompare(b);
    });
}
