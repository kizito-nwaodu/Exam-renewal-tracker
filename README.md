# MSFT Exam Tracker — Webapp (Local-first)

A lightweight, **static** web application to track your Microsoft certifications and exams across **Fundamentals, Associate, Expert/Specialty**, with statuses like **Planned, Scheduled, Passed (Active/Expired), Retired**. Data is stored **locally in your browser** (LocalStorage). No backend required.

## Features
- Add/edit/delete certifications and exams
- Filter by **Level** and **Status**, search, and sort
- Dashboard cards (Totals, Active, Scheduled, Expired, Retired)
- Renewal countdown badges (color-coded: green/amber/red)
- **Import/Export** JSON (and CSV with a simple header mapping)
- Mobile responsive; deployable to **GitHub Pages** or **Vercel** in seconds

## Quick Start
1. Open `index.html` in a browser, or deploy (see below).
2. Click **+ Add** to create entries, or **Import** to load your existing data (JSON/CSV).
3. Use filters and search to find items quickly.
4. Use **Export** regularly to back up your data.

## CSV Template
You can import CSV with headers matching the following (first row):
```
Certification / Exam Name,Exam Code(s),Level,Status,Date Passed,Expiration Date,Renewal Due (months),Role / Domain,Source Link,Notes
```

## Mapping to Microsoft Learn Transcript
Microsoft Learn lets you **view, share, and print** your transcript from your profile. You can **Share link** to create a public URL with an access code, or **Print → Save to PDF** to export. This app doesn’t call Microsoft APIs; paste/import your data manually for now. See Microsoft’s docs: *Access certificates, badges, and transcript* and *View and share your transcript*.

## Deploy
- **GitHub Pages:** push this folder to a repo and enable Pages (root). Open the Pages URL.
- **Vercel/Netlify:** drag-and-drop the folder or connect your repo. No build step required.

## Data Model
Each item is stored as:
```json
{
  "id": "uuid",
  "name": "Security Operations Analyst Associate",
  "codes": "SC-200",
  "level": "Associate",
  "status": "Passed (Active)",
  "datePassed": "2025-08-15",
  "expiration": "2026-08-15",
  "renewal": 12,
  "domain": "Security / XDR",
  "source": "https://learn.microsoft.com/certifications/exams/sc-200/",
  "notes": "Renew via free assessment before expiry"
}
```

## Roadmap (optional)
- **Transcript Import Wizard:** paste text copied from the Learn transcript page/PDF → parse with regex
- **Retired Exam Auto-tagging:** maintain a JSON of retired codes and flag items
- **Calendar export:** generate .ics reminders for renewals
- **Cloud sync:** optional Supabase/SQLite backend

## Privacy
This app is local-first. Your data stays in your browser unless you export it yourself.
