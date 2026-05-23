const fs   = require('fs');
const path = require('path');

const DB_FILE  = path.join(__dirname, 'data.json');
const REDIS_KEY = 'family_planner_data';

function useRedis() {
  return !!(process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN);
}

function getRedis() {
  const { Redis } = require('@upstash/redis');
  return new Redis({
    url:   process.env.UPSTASH_REDIS_REST_URL,
    token: process.env.UPSTASH_REDIS_REST_TOKEN,
  });
}

async function read() {
  if (useRedis()) {
    const data = await getRedis().get(REDIS_KEY);
    return data || { nextId: 1, submissions: [] };
  }
  if (!fs.existsSync(DB_FILE)) return { nextId: 1, submissions: [] };
  return JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
}

async function write(data) {
  if (useRedis()) {
    await getRedis().set(REDIS_KEY, data);
    return;
  }
  fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), 'utf8');
}

module.exports = {
  async insertSubmission(row) {
    const data = await read();
    const record = { id: data.nextId++, ...row, submitted_at: new Date().toISOString().slice(0, 19) };
    data.submissions.push(record);
    await write(data);
    return record;
  },

  async getAllSubmissions() {
    return (await read()).submissions;
  },

  async deleteSubmission(id) {
    const data = await read();
    data.submissions = data.submissions.filter(s => s.id !== id);
    await write(data);
  },
};
