IF OBJECT_ID('dbo.Customers', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Customers (
        customer_id     INT             NOT NULL PRIMARY KEY,
        first_name      NVARCHAR(100)   NULL,
        last_name       NVARCHAR(100)   NULL,
        email           NVARCHAR(255)   NULL,
        phone           NVARCHAR(50)    NULL,
        government_id   NVARCHAR(11)    NULL,
        date_of_birth   DATE            NULL,
        address         NVARCHAR(255)   NULL,
        created_at      DATETIME2(3)    NOT NULL CONSTRAINT DF_Customers_created_at DEFAULT SYSUTCDATETIME(),
        updated_at      DATETIME2(3)    NOT NULL CONSTRAINT DF_Customers_updated_at DEFAULT SYSUTCDATETIME(),
        is_deleted      BIT             NOT NULL CONSTRAINT DF_Customers_is_deleted DEFAULT 0
    );

    CREATE INDEX IX_Customers_updated_at ON dbo.Customers (updated_at);
    CREATE INDEX IX_Customers_government_id ON dbo.Customers (government_id);
    CREATE INDEX IX_Customers_email ON dbo.Customers (email);
END
