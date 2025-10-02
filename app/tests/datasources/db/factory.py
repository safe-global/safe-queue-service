import random

from eth_account import Account
from faker import Faker
from hexbytes import HexBytes

from app.datasources.db.models import MultisigTransaction, SafeOperationEnum

fake = Faker()

COMMON_CHAIN_IDS = [1, 5, 10, 56, 137, 42161, 11155111]


async def multisig_transaction_factory(
    safe_tx_hash: bytes | None = None,
    chain_id: int | None = None,
    safe: bytes | str | None = None,
    nonce: int | None = None,
    proposer: bytes | str | None = None,
    proposed_by_delegate: bytes | str | None = None,
    tx_hash: bytes | None = None,
    to: bytes | str | None = None,
    value: int | None = None,
    data: bytes | None = None,
    operation: SafeOperationEnum | None = None,
    safe_tx_gas: int | None = None,
    base_gas: int | None = None,
    gas_price: int | None = None,
    gas_token: bytes | None = None,
    refund_receiver: bytes | None = None,
    signatures: bytes | None = None,
    failed: bool | None = None,
    origin: dict | None = None,
) -> MultisigTransaction:
    transaction = MultisigTransaction(
        safe_tx_hash=safe_tx_hash
        or random.randbytes(32)
        or HexBytes(Account.create().address).rjust(32, b"\0"),
        chain_id=(chain_id or random.choice(COMMON_CHAIN_IDS)),
        safe=HexBytes(safe if safe else "") or HexBytes(Account.create().address),
        nonce=nonce if nonce is not None else random.randint(0, 2**32 - 1),
        proposer=HexBytes(proposer if proposer else ""),
        proposed_by_delegate=HexBytes(
            proposed_by_delegate if proposed_by_delegate else ""
        ),
        tx_hash=tx_hash,
        to=HexBytes(to if to else ""),
        value=value if value is not None else random.randint(0, 2**64 - 1),
        data=data,
        operation=operation or SafeOperationEnum.CALL,
        safe_tx_gas=(
            safe_tx_gas if safe_tx_gas is not None else random.randint(1, 2**32 - 1)
        ),
        base_gas=base_gas if base_gas is not None else random.randint(1, 2**32 - 1),
        gas_price=gas_price if gas_price is not None else random.randint(1, 2**32 - 1),
        gas_token=gas_token,
        refund_receiver=refund_receiver,
        signatures=signatures,
        failed=failed,
        origin=origin or {},
    )
    return await transaction.create()
