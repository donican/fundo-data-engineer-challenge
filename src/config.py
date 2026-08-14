import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class SqlServerConfig:
    host: str
    port: str
    database: str
    user: str
    password: str

    @property
    def sqlalchemy_url(self) -> str:
        driver = "ODBC Driver 18 for SQL Server".replace(" ", "+")
        return (
            f"mssql+pyodbc://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
            f"?driver={driver}&Encrypt=yes&TrustServerCertificate=yes"
        )


def load_sqlserver_config() -> SqlServerConfig:
    return SqlServerConfig(
        host=os.environ["SQLSERVER_HOST"],
        port=os.environ.get("SQLSERVER_PORT", "1433"),
        database=os.environ.get("SQLSERVER_DATABASE", "master"),
        user=os.environ.get("SQLSERVER_USER", "sa"),
        password=os.environ["SQLSERVER_PASSWORD"],
    )


def load_duckdb_path() -> str:
    return os.environ.get("DUCKDB_PATH", "data/warehouse.duckdb")
