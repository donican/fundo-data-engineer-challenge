IF OBJECT_ID('dbo.Transactions', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Transactions (
        transaction_id  BIGINT          NOT NULL PRIMARY KEY, -- app-assigned, not IDENTITY (see SOLUTION.md); BIGINT since this is the largest, fastest-growing table
        customer_id     INT             NOT NULL CONSTRAINT FK_Transactions_Customers REFERENCES dbo.Customers (customer_id),
        card_id         INT             NOT NULL CONSTRAINT FK_Transactions_Cards REFERENCES dbo.Cards (card_id),
        item            NVARCHAR(255)   NOT NULL,
        value           DECIMAL(18, 2)  NOT NULL,
        occurred_at     DATETIME2(3)    NOT NULL,
        created_at      DATETIME2(3)    NOT NULL CONSTRAINT DF_Transactions_created_at DEFAULT SYSUTCDATETIME(),
        updated_at      DATETIME2(3)    NOT NULL CONSTRAINT DF_Transactions_updated_at DEFAULT SYSUTCDATETIME() -- CDC watermark: the incremental extractor filters/orders on this column (see SOLUTION.md)
    );

    CREATE INDEX IX_Transactions_updated_at ON dbo.Transactions (updated_at);
    CREATE INDEX IX_Transactions_customer_id ON dbo.Transactions (customer_id);
    CREATE INDEX IX_Transactions_card_id ON dbo.Transactions (card_id);
    CREATE INDEX IX_Transactions_occurred_at ON dbo.Transactions (occurred_at);
END
