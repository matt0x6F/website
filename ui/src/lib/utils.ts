// function that converts to bytes to KB, MB, GB, TB
export function formatBytes(bytes: number, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

export function formatCharset(charset: string | null) {
    if (charset === null) return 'N/A';
    return charset;
}

export function iso8601String(date: Date | null | undefined): string {
    if (!date) {
        return "";
    }
    
    return date.toISOString();
}

export function formatDate(date: Date | null | undefined): string {
    if (!date) {
        return "";
    }

    // change date to the user's local timezone
    const offset = new Date().getTimezoneOffset();
    const localDate = new Date(date.getTime() - offset * 60000);
    
    const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

    const dayOfWeek = daysOfWeek[localDate.getDay()];
    const month = months[localDate.getMonth()];
    const day = localDate.getDate();
    const year = localDate.getFullYear();
    const hours = String(localDate.getHours()).padStart(2, '0');
    const minutes = String(localDate.getMinutes()).padStart(2, '0');

    // Function to get the correct ordinal suffix
    function getOrdinalSuffix(day: number): string {
        if (day > 3 && day < 21) return 'th'; // Handles 11th, 12th, 13th
        switch (day % 10) {
            case 1: return 'st';
            case 2: return 'nd';
            case 3: return 'rd';
            default: return 'th';
        }
    }

    const dayWithSuffix = day + getOrdinalSuffix(day);

    // store a value with the timezone
    const timezone = localDate.getTimezoneOffset() / 60;

    return `${dayOfWeek}, ${month} the ${dayWithSuffix}, ${year} @ ${hours}:${minutes} (UTC${timezone >= 0 ? "+" : "-"}${timezone})`;
}

export function parseDateAsYear(date: Date | null | undefined): string {
    if (!date) {
        return "";
    }
    
    return date.getFullYear().toString();
}