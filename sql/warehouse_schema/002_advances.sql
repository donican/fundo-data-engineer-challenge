CREATE TABLE IF NOT EXISTS advances (
    advance_id      INTEGER         NOT NULL PRIMARY KEY,
    customer_id     INTEGER         NOT NULL,
    amount          DECIMAL(18, 2)  NOT NULL,
    status          VARCHAR         NOT NULL,
    created_at      TIMESTAMP       NOT NULL,
    updated_at      TIMESTAMP       NOT NULL
);
