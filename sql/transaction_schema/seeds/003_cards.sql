IF NOT EXISTS (SELECT 1 FROM dbo.Cards)
BEGIN
    ;WITH Numbers AS (
        SELECT 1 AS n
        UNION ALL
        SELECT n + 1 FROM Numbers WHERE n < 6000
    )
    INSERT INTO dbo.Cards (card_id, customer_id, card_number, status, created_at, updated_at)
    SELECT
        n AS card_id,
        CASE WHEN n <= 5000 THEN n ELSE n - 5000 END AS customer_id,
        '4000' + RIGHT('000000000000' + CAST(n AS VARCHAR(12)), 12) AS card_number,
        CASE
            WHEN n % 10 < 8 THEN 'active'
            WHEN n % 10 < 9 THEN 'inactive'
            ELSE 'blocked'
        END AS status,
        DATEADD(MINUTE, -(6000 - n) * 10, SYSUTCDATETIME()) AS created_at,
        DATEADD(MINUTE, -(6000 - n) * 10, SYSUTCDATETIME()) AS updated_at
    FROM Numbers
    OPTION (MAXRECURSION 0);
END
