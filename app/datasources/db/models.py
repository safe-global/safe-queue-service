import datetime
from enum import IntEnum

from sqlalchemy import DateTime, Index, SmallInteger, desc
from sqlmodel import (
    JSON,
    Column,
    Field,
    SQLModel,
    select,
)

from .database import db_session
from .fields import EthereumAddressType, EthereumHashType, Uint256Type


class SqlQueryBase:
    @classmethod
    async def get_all(cls):
        result = await db_session.execute(select(cls))
        return result.scalars().all()

    async def _save(self):
        db_session.add(self)
        await db_session.commit()
        return self

    async def update(self):
        return await self._save()

    async def create(self):
        return await self._save()


class TimeStampedSQLModel(SQLModel):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.

    """

    created: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
        sa_type=DateTime(timezone=True),  # type: ignore
        index=True,
    )

    modified: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={
            "onupdate": lambda: datetime.datetime.now(datetime.UTC),
        },
    )


class SafeOperationEnum(IntEnum):
    CALL = 0
    DELEGATE_CALL = 1
    CREATE = 2
    CREATE2 = 3


class MultisigTransaction(SqlQueryBase, TimeStampedSQLModel, table=True):
    __table_args__ = (
        Index(
            "ix__multisigtransaction_safe_sorted",
            "safe",
            desc("nonce"),
            desc("created"),
        ),
    )

    safe_tx_hash: bytes = Field(
        sa_column=Column(EthereumHashType(), nullable=False, primary_key=True)
    )
    chain_id: int = Field(sa_column=Column(Uint256Type(), nullable=False))
    safe: bytes = Field(
        sa_column=Column(EthereumAddressType(), nullable=False, index=True)
    )
    nonce: int = Field(sa_column=Column(Uint256Type(), nullable=False, index=True))
    proposer: bytes | None = Field(
        default=None,
        sa_column=Column(EthereumAddressType(), nullable=True),
    )
    proposed_by_delegate: bytes | None = Field(
        default=None,
        sa_column=Column(EthereumAddressType(), nullable=True),
    )
    to: bytes | None = Field(
        default=None,
        sa_column=Column(EthereumAddressType(), nullable=True, index=True),
    )  # `None` = ETHEREUM_ZERO_ADDRESS
    value: int = Field(sa_column=Column(Uint256Type(), nullable=False))
    data: bytes | None = Field(default=None)
    operation: SafeOperationEnum = Field(sa_column=Column(SmallInteger, nullable=False))
    safe_tx_gas: int = Field(sa_column=Column(Uint256Type(), nullable=False))
    base_gas: int = Field(sa_column=Column(Uint256Type(), nullable=False))
    gas_price: int = Field(sa_column=Column(Uint256Type(), nullable=False))
    gas_token: bytes | None = Field(
        default=None,
        sa_column=Column(EthereumAddressType(), nullable=True),
    )  # `None` = ETHEREUM_ZERO_ADDRESS
    refund_receiver: bytes | None = Field(
        default=None,
        sa_column=Column(EthereumAddressType(), nullable=True),
    )  # `None` = ETHEREUM_ZERO_ADDRESS
    signatures: bytes | None = Field(default=None)
    failed: bool | None = Field(default=None, index=True)
    origin: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # Optional executed tx hash
    tx_hash: bytes | None = Field(sa_column=Column(EthereumHashType(), nullable=True))
