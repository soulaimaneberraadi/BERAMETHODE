const Database = require('better-sqlite3');
const db = new Database('./database.sqlite');
const table = db.prepare("SELECT sql FROM sqlite_master WHERE name='app_settings'").get();
console.log(table ? table.sql : 'NOT FOUND');
