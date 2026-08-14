IF OBJECT_ID('dbo.Cards', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Cards (
        card_id         INT             NOT NULL PRIMARY KEY, -- app-assigned, not IDENTITY (see SOLUTION.md)
        customer_id     INT             NOT NULL CONSTRAINT FK_Cards_Customers REFERENCES dbo.Customers (customer_id),
        card_number     NVARCHAR(20)    NOT NULL,
        status          NVARCHAR(20)    NOT NULL, -- e.g. 'active' | 'inactive' | 'blocked'
        created_at      DATETIME2(3)    NOT NULL CONSTRAINT DF_Cards_created_at DEFAULT SYSUTCDATETIME(),
        updated_at      DATETIME2(3)    NOT NULL CONSTRAINT DF_Cards_updated_at DEFAULT SYSUTCDATETIME()
    );

    CREATE INDEX IX_Cards_customer_id ON dbo.Cards (customer_id);
    CREATE INDEX IX_Cards_updated_at ON dbo.Cards (updated_at);
    CREATE INDEX IX_Cards_card_number ON dbo.Cards (card_number);
END
