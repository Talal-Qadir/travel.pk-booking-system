import { getPartnerKey, setPartnerKey } from '../services/api'
import { useState } from 'react'

export function Navbar() {
  const [key, setKey] = useState(getPartnerKey())
  const [saved, setSaved] = useState(false)

  function saveKey() {
    setPartnerKey(key.trim())
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <header className="border-b border-slate-200 bg-white px-6 py-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-semibold text-slate-900">Travel.pk Admin</h1>
          <p className="text-sm text-slate-500">Booking & payment operations console</p>
        </div>
        <div className="flex items-end gap-2">
          <label className="text-xs text-slate-500">
            Partner API key
            <input
              className="mt-1 block w-56 rounded-md border border-slate-300 px-2 py-1.5 text-sm"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="partner-admin"
            />
          </label>
          <button
            type="button"
            onClick={saveKey}
            className="rounded-md bg-sky-600 px-3 py-2 text-sm font-medium text-white hover:bg-sky-700"
          >
            Save
          </button>
          {saved ? <span className="text-xs text-emerald-600">Saved</span> : null}
        </div>
      </div>
    </header>
  )
}
