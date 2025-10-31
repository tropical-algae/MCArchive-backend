from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, Text
from sqlmodel import Column, Field, SQLModel


class Archives(SQLModel, table=True):
    id: str | None = Field(default=None, sa_column=Column("id", Text, primary_key=True))
    server_file: str = Field(sa_column=Column("server_file", Text))
    server_name: str = Field(sa_column=Column("server_name", Text))
    server_status: bool = Field(sa_column=Column("server_status", Boolean))
    created_at: datetime = Field(sa_column=Column("created_at", DateTime))
    updated_at: datetime = Field(sa_column=Column("updated_at", DateTime))
    port: str | None = Field(default=None, sa_column=Column("port", Text))
    modpack_name: str | None = Field(default=None, sa_column=Column("modpack_name", Text))
    snapshot_name: str | None = Field(
        default=None, sa_column=Column("snapshot_name", Text)
    )
    snapshot_date: datetime | None = Field(
        default=None, sa_column=Column("snapshot_date", DateTime)
    )


class Tokens(SQLModel, table=True):
    id: int | None = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    token: str = Field(sa_column=Column("token", Text))
    is_admin: bool = Field(sa_column=Column("is_admin", Boolean))
    is_activated: bool = Field(sa_column=Column("is_activated", Boolean))
