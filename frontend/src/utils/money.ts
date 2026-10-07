export function formatPaisa(paisa: number, currency = 'PKR'): string {
  const sign = paisa < 0 ? '-' : ''
  const abs = Math.abs(paisa)
  const whole = Math.floor(abs / 100)
  const fraction = abs % 100
  const wholeFormatted = whole.toLocaleString('en-PK')
  const fractionFormatted = fraction.toString().padStart(2, '0')
  return `${sign}${currency} ${wholeFormatted}.${fractionFormatted}`
}
