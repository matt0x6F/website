export function getWeekIndex(day: string, firstDay: string): number {
  const firstDate = new Date(firstDay + 'T00:00:00Z');
  const thisDate = new Date(day + 'T00:00:00Z');
  // Align firstDate to the previous Sunday
  const firstDayOfWeek = firstDate.getDay(); // 0 = Sunday
  const alignedFirstDate = new Date(firstDate);
  alignedFirstDate.setDate(firstDate.getDate() - firstDayOfWeek);
  // Calculate difference in days from aligned first date
  const diffDays = Math.floor((thisDate.getTime() - alignedFirstDate.getTime()) / (1000 * 60 * 60 * 24));
  return Math.floor(diffDays / 7);
} 