export const formatDurationMinutes = (minutes: number): string => {
  const safeMinutes = Number.isFinite(minutes) ? Math.max(0, Math.floor(minutes)) : 0;
  const hours = Math.floor(safeMinutes / 60);
  const remainingMinutes = safeMinutes % 60;

  if (hours === 0) {
    const minuteLabel = remainingMinutes === 1 ? 'minute' : 'minutes';
    return `${remainingMinutes}${minuteLabel}`;
  }

  if (remainingMinutes === 0) {
    return `${hours}h`;
  }

  const minuteLabel = remainingMinutes === 1 ? 'minute' : 'minutes';
  return `${hours}h ${remainingMinutes}${minuteLabel}`;
};

export const formatDurationFromMilliseconds = (milliseconds: number): string => {
  const minutes = Math.floor(Math.max(0, milliseconds) / 60000);
  return formatDurationMinutes(minutes);
};

export const toLocalDateTimePayload = (date: Date): string => {
  const pad = (value: number) => String(value).padStart(2, '0');
  return [
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`,
    `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`,
  ].join('T');
};
