CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  BIGINT          NOT NULL PRIMARY KEY,
    customer_id     INTEGER         NOT NULL,
    card_id         INTEGER         NOT NULL,
    item            VARCHAR         NOT NULL,
    value           DECIMAL(18, 2)  NOT NULL,
    occurred_at     TIMESTAMP       NOT NULL,
    created_at      TIMESTAMP       NOT NULL,
    updated_at      TIMESTAMP       NOT NULL
);
