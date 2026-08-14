DECLARE @batch_size INT = (SELECT CAST(COUNT(*) * 0.01 AS INT) FROM dbo.Transactions); -- ~1% of current volume
DECLARE @new_count INT = @batch_size / 2;
DECLARE @update_count INT = @batch_size - @new_count;
DECLARE @max_id BIGINT = (SELECT MAX(transaction_id) FROM dbo.Transactions);
DECLARE @max_card_id INT = (SELECT MAX(card_id) FROM dbo.Cards);

-- New transactions
;WITH Numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM Numbers WHERE n < @new_count
)
INSERT INTO dbo.Transactions (transaction_id, customer_id, card_id, item, value, occurred_at, created_at, updated_at)
SELECT
    @max_id + Numbers.n AS transaction_id,
    c.customer_id,
    c.card_id,
    'Item ' + CAST(1 + (Numbers.n % 50) AS VARCHAR(10)) AS item,
    CAST(5 + (Numbers.n % 200) * 3.47 AS DECIMAL(18, 2)) AS value,
    SYSUTCDATETIME() AS occurred_at,
    SYSUTCDATETIME() AS created_at,
    SYSUTCDATETIME() AS updated_at
FROM Numbers
JOIN dbo.Cards c ON c.card_id = ((Numbers.n - 1) % @max_card_id) + 1
OPTION (MAXRECURSION 0);


;WITH ToUpdate AS (
    SELECT TOP (@update_count) transaction_id
    FROM dbo.Transactions
    ORDER BY NEWID()
)
UPDATE t
SET t.value = t.value + 1.00,
    t.updated_at = SYSUTCDATETIME()
FROM dbo.Transactions t
JOIN ToUpdate u ON u.transaction_id = t.transaction_id;
