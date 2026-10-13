CREATE TABLE IF NOT EXISTS holdings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code   TEXT    NOT NULL UNIQUE,
    shares      REAL,
    cost_nav    REAL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS reports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id   TEXT    NOT NULL,
    version     INTEGER NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'pending',
    content     TEXT    NOT NULL,
    feedback    TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    UNIQUE (thread_id, version)
);
