require('dotenv').config();
const express = require('express');
const session = require('express-session');
const path = require('path');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'family2026';
const SESSION_SECRET = process.env.SESSION_SECRET || 'family-planner-dev-secret';

const HOLIDAYS = [
  { id: 'christmas_2026', label: "Christmas & New Year's", period: 'Dec 2026 – Jan 2027' },
  { id: 'easter_2027',    label: 'Easter',                  period: 'April 2027' },
  { id: 'school_mid_2027', label: 'Mid-year school break',  period: 'June / July 2027' },
  { id: 'christmas_2027', label: "Christmas & New Year's",  period: 'Dec 2027 – Jan 2028' },
  { id: 'easter_2028',    label: 'Easter',                  period: 'March / April 2028' },
  { id: 'school_mid_2028', label: 'Mid-year school break',  period: 'June / July 2028' },
  { id: 'baby_first_visit', label: "Meeting the new baby",  period: 'Oct / Nov 2026' },
  { id: 'baby_bday_2027', label: "Baby's first birthday",   period: 'September 2027' },
];

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(session({
  secret: SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 8 * 60 * 60 * 1000 }, // 8 hours
}));
app.use(express.static(path.join(__dirname, 'public')));

function requireAdmin(req, res, next) {
  if (req.session.isAdmin) return next();
  res.status(401).json({ error: 'Not authenticated' });
}

// Form submission
app.post('/submit', (req, res) => {
  const body = req.body;

  const holidayPriorities = {};
  for (const h of HOLIDAYS) {
    holidayPriorities[h.id] = body[`priority_${h.id}`] || 'no';
  }

  const availability = [];
  for (let i = 1; i <= 3; i++) {
    const start = body[`avail_start_${i}`];
    const end   = body[`avail_end_${i}`];
    if (start && end) {
      availability.push({ start, end, notes: body[`avail_notes_${i}`] || '' });
    }
  }

  db.insertSubmission({
    name:              body.name?.trim() || 'Unknown',
    family_group:      body.family_group || 'other',
    holiday_priorities: JSON.stringify(holidayPriorities),
    availability:      JSON.stringify(availability),
    can_travel:        body.can_travel ? 1 : 0,
    can_host:          body.can_host   ? 1 : 0,
    preferred_location: body.preferred_location?.trim() || '',
    special_events:    body.special_events?.trim() || '',
    other_notes:       body.other_notes?.trim() || '',
  });

  res.redirect('/thanks.html');
});

// Admin auth
app.post('/admin/login', (req, res) => {
  if (req.body.password === ADMIN_PASSWORD) {
    req.session.isAdmin = true;
    res.redirect('/admin.html');
  } else {
    res.redirect('/admin.html?error=1');
  }
});

app.get('/admin/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/admin.html');
});

// Admin API
app.get('/api/auth-check', (req, res) => {
  res.json({ ok: !!req.session.isAdmin });
});

app.get('/api/submissions', requireAdmin, (req, res) => {
  res.json(db.getAllSubmissions());
});

app.delete('/api/submissions/:id', requireAdmin, (req, res) => {
  db.deleteSubmission(Number(req.params.id));
  res.json({ ok: true });
});

app.get('/api/export.csv', requireAdmin, (req, res) => {
  const rows = db.getAllSubmissions();
  const holidayHeaders = HOLIDAYS.map(h => `"${h.label} (${h.period})"`).join(',');
  const header = `Name,Family Group,Submitted,${holidayHeaders},Can Travel,Can Host,Preferred Location,Special Events,Notes\n`;

  const lines = rows.map(r => {
    const priorities = JSON.parse(r.holiday_priorities || '{}');
    const hCols = HOLIDAYS.map(h => `"${priorities[h.id] || 'no'}"`).join(',');
    return [
      `"${r.name}"`,
      `"${r.family_group}"`,
      `"${r.submitted_at}"`,
      hCols,
      r.can_travel ? 'Yes' : 'No',
      r.can_host   ? 'Yes' : 'No',
      `"${r.preferred_location}"`,
      `"${(r.special_events || '').replace(/"/g, '""')}"`,
      `"${(r.other_notes   || '').replace(/"/g, '""')}"`,
    ].join(',');
  });

  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="family-planner.csv"');
  res.send(header + lines.join('\n'));
});

app.listen(PORT, () => {
  console.log(`Family planner running at http://localhost:${PORT}`);
  console.log(`  Form:  http://localhost:${PORT}/form.html`);
  console.log(`  Admin: http://localhost:${PORT}/admin.html`);
});
