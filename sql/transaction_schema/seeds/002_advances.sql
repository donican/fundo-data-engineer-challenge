IF NOT EXISTS (SELECT 1 FROM dbo.Advances)
BEGIN
    ;WITH Numbers AS (
        SELECT 1 AS n
        UNION ALL
        SELECT n + 1 FROM Numbers WHERE n < 2000
    )
    INSERT INTO dbo.Advances (advance_id, customer_id, amount, status, created_at, updated_at)
    SELECT
        n AS advance_id,
        n AS customer_id,
        CAST(500 + (n % 50) * 97.35 AS DECIMAL(18, 2)) AS amount,
        CASE
            WHEN n % 20 < 12 THEN 'funded'
            WHEN n % 20 < 17 THEN 'paid_off'
            ELSE 'canceled'
        END AS status,
        DATEADD(MINUTE, -(2000 - n) * 10, SYSUTCDATETIME()) AS created_at,
        DATEADD(MINUTE, -(2000 - n) * 10, SYSUTCDATETIME()) AS updated_at
    FROM Numbers
    OPTION (MAXRECURSION 0);
END
