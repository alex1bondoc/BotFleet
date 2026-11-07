CREATE TABLE IF NOT EXISTS games (
    id           UUID PRIMARY KEY,
    status       VARCHAR(20)  NOT NULL DEFAULT 'pending',
    seed         INTEGER      NOT NULL,
    bot1_path    TEXT         NOT NULL,
    bot2_path    TEXT         NOT NULL,
    history_path TEXT,
    winner       INTEGER,
    error        TEXT,
    created_at   TIMESTAMP    NOT NULL,
    updated_at   TIMESTAMP    NOT NULL
);
