const fs   = require('fs');
const path = require('path');

const DB_FILE = path.join(__dirname, 'data.json');

function read() {
  if (!fs.existsSync(DB_FILE)) return { nextId: 1, submissions: [] };
  return JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
}

function write(data) {
  fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), 'utf8');
}

module.exports = {
  insertSubmission(row) {
    const data = read();
    const record = { id: data.nextId++, ...row, submitted_at: new Date().toISOString().slice(0, 19) };
    data.submissions.push(record);
    write(data);
    return record;
  },

  getAllSubmissions() {
    return read().submissions;
  },

  deleteSubmission(id) {
    const data = read();
    data.submissions = data.submissions.filter(s => s.id !== id);
    write(data);
  },
};
