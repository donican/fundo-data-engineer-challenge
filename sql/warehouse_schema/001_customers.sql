CREATE TABLE IF NOT EXISTS customers (
    customer_id     INTEGER         NOT NULL PRIMARY KEY,
    first_name      VARCHAR         NULL,
    last_name       VARCHAR         NULL,
    email           VARCHAR         NULL,
    phone           VARCHAR         NULL,
    government_id   VARCHAR         NULL,
    date_of_birth   DATE            NULL,
    address         VARCHAR         NULL,
    created_at      TIMESTAMP       NOT NULL,
    updated_at      TIMESTAMP       NOT NULL
);
