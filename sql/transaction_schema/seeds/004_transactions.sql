IF NOT EXISTS (SELECT 1 FROM dbo.Transactions)
BEGIN
    ;WITH Numbers AS (
        SELECT 1 AS n
        UNION ALL
        SELECT n + 1 FROM Numbers WHERE n < 100000
    ),
    Rows AS (
        SELECT
            n,
            ((n - 1) % 6000) + 1 AS card_id,
            DATEADD(MINUTE, -(100000 - n) * 2, SYSUTCDATETIME()) AS base_ts
        FROM Numbers
    )
    INSERT INTO dbo.Transactions (
        transaction_id, customer_id, card_id, item, value, occurred_at, created_at, updated_at
    )
    SELECT
        n AS transaction_id,
        CASE WHEN card_id <= 5000 THEN card_id ELSE card_id - 5000 END AS customer_id,
        card_id,
        'Item ' + CAST(1 + (n % 50) AS VARCHAR(10)) AS item,
        CAST(5 + (n % 200) * 3.47 AS DECIMAL(18, 2)) AS value,
        base_ts AS occurred_at,
        base_ts AS created_at,
        CASE WHEN n % 500 = 0 THEN LEAST(DATEADD(DAY, 1, base_ts), SYSUTCDATETIME()) ELSE base_ts END AS updated_at
    FROM Rows
    OPTION (MAXRECURSION 0);
END
