CREATE TABLE IF NOT EXISTS dedup_groups (
    group_id                INTEGER     NOT NULL PRIMARY KEY,
    evidence_type           VARCHAR     NOT NULL, -- always 'government_id' today;
    status                  VARCHAR     NOT NULL, -- 'merged' | 'needs_review'
    survivor_customer_id    INTEGER     NULL,     -- NULL when status = 'needs_review'
    reason                  VARCHAR     NOT NULL,
    member_count            INTEGER     NOT NULL,
    protected_member_count  INTEGER     NOT NULL,
    decided_at              TIMESTAMP   NOT NULL
);
