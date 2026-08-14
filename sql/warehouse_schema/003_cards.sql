CREATE TABLE IF NOT EXISTS cards (
    card_id         INTEGER         NOT NULL PRIMARY KEY,
    customer_id     INTEGER         NOT NULL,
    card_number     VARCHAR         NOT NULL,
    status          VARCHAR         NOT NULL,
    created_at      TIMESTAMP       NOT NULL,
    updated_at      TIMESTAMP       NOT NULL
);
