IF OBJECT_ID('dbo.Advances', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Advances (
        advance_id      INT             NOT NULL PRIMARY KEY, -- app-assigned, not IDENTITY (see SOLUTION.md)
        customer_id     INT             NOT NULL CONSTRAINT FK_Advances_Customers REFERENCES dbo.Customers (customer_id),
        amount          DECIMAL(18, 2)  NOT NULL,
        status          NVARCHAR(20)    NOT NULL, -- 'funded' | 'paid_off' | 'canceled' -- funded/paid_off are untouchable (see SOLUTION.md); only canceled is mergeable
        created_at      DATETIME2(3)    NOT NULL CONSTRAINT DF_Advances_created_at DEFAULT SYSUTCDATETIME(),
        updated_at      DATETIME2(3)    NOT NULL CONSTRAINT DF_Advances_updated_at DEFAULT SYSUTCDATETIME()
    );

    CREATE INDEX IX_Advances_customer_id ON dbo.Advances (customer_id);
    CREATE INDEX IX_Advances_updated_at ON dbo.Advances (updated_at);
    CREATE INDEX IX_Advances_status ON dbo.Advances (status);
END
