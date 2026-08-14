CREATE TABLE IF NOT EXISTS dedup_group_members (
    group_id      INTEGER     NOT NULL,
    customer_id   INTEGER     NOT NULL,
    is_protected  BOOLEAN     NOT NULL,
    is_survivor   BOOLEAN     NOT NULL, 
    PRIMARY KEY (group_id, customer_id)
);
