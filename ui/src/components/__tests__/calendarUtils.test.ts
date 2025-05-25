import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getWeekIndex } from '../calendarUtils';

describe('getWeekIndex', () => {
  it('places the first day in week 0', () => {
    expect(getWeekIndex('2024-05-01', '2024-05-01')).toBe(0);
  });

  it('places the next day in the same week if not Sunday', () => {
    expect(getWeekIndex('2024-05-02', '2024-05-01')).toBe(0);
  });

  it('places a day 7 days later in week 1', () => {
    expect(getWeekIndex('2024-05-08', '2024-05-01')).toBe(1);
  });

  it('places today in the correct week', () => {
    const today = new Date();
    const firstDay = new Date(today);
    firstDay.setDate(today.getDate() - 364);
    const firstDayStr = firstDay.toISOString().slice(0, 10);
    const todayStr = today.toISOString().slice(0, 10);
    // Should be week 52 (if 365 days, 52 weeks + 1 day), but now aligned to previous Sunday
    const alignedFirstDay = new Date(firstDay);
    alignedFirstDay.setDate(firstDay.getDate() - firstDay.getDay());
    const diffDays = Math.floor((today.getTime() - alignedFirstDay.getTime()) / (1000 * 60 * 60 * 24));
    expect(getWeekIndex(todayStr, firstDayStr)).toBe(Math.floor(diffDays / 7));
  });
}); 