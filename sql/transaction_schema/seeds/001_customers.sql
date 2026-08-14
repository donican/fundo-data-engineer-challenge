IF NOT EXISTS (SELECT 1 FROM dbo.Customers)
BEGIN
    ;WITH Numbers AS (
        SELECT 1 AS n
        UNION ALL
        SELECT n + 1 FROM Numbers WHERE n < 5000
    ),
    Rows AS (
        SELECT
            n,
            CASE WHEN n % 50 = 0 AND n > 1 THEN n - 1 ELSE n END AS document_owner
        FROM Numbers
    )
    INSERT INTO dbo.Customers (
        customer_id, first_name, last_name, email, phone,
        government_id, date_of_birth, address, created_at, updated_at
    )
    SELECT
        n AS customer_id,
        'First' + CAST(n AS VARCHAR(10)) AS first_name,
        'Last' + CAST(n AS VARCHAR(10)) AS last_name,
        'customer' + CAST(n AS VARCHAR(10)) + '@example.com' AS email,
        '+55119' + RIGHT('00000000' + CAST(n AS VARCHAR(10)), 8) AS phone,
        RIGHT('00000000000' + CAST(document_owner AS VARCHAR(11)), 11) AS government_id,
        DATEFROMPARTS(1950 + (n % 60), 1 + (n % 12), 1 + (n % 28)) AS date_of_birth,
        'Rua Exemplo, ' + CAST(n AS VARCHAR(10)) AS address,
        DATEADD(MINUTE, -(5000 - n) * 10, SYSUTCDATETIME()) AS created_at,
        DATEADD(MINUTE, -(5000 - n) * 10, SYSUTCDATETIME()) AS updated_at
    FROM Rows
    OPTION (MAXRECURSION 5000);
END
