from __future__ import annotations

from sqlalchemy import select

from app.datasources.db.database import db_session, db_session_context
from app.datasources.db.models import MultisigTransaction, SafeOperationEnum
from app.tests.datasources.db.async_db_test_case import AsyncDbTestCase
from app.tests.datasources.db.factory import multisig_transaction_factory


class TestMultisigTransaction(AsyncDbTestCase):
    @db_session_context
    async def test_create_and_get_all(self) -> None:
        transaction = await multisig_transaction_factory(
            nonce=7,
            value=123456,
            operation=SafeOperationEnum.CALL,
            safe_tx_gas=21000,
            base_gas=10,
            gas_price=50,
            signatures=b"signed",
            failed=False,
            origin={"type": "create"},
        )

        results = await MultisigTransaction.get_all()
        assert len(results) == 1
        stored = results[0]

        assert stored.safe_tx_hash == transaction.safe_tx_hash
        assert stored.safe == transaction.safe
        assert stored.proposer == transaction.proposer
        assert stored.to == transaction.to
        assert stored.nonce == 7
        assert stored.value == 123456
        assert stored.operation == SafeOperationEnum.CALL
        assert stored.signatures == b"signed"
        assert stored.origin == {"type": "create"}

    @db_session_context
    async def test_retrieve_by_safe_address(self) -> None:
        shared_safe_tx = await multisig_transaction_factory(nonce=1)
        await multisig_transaction_factory(safe=None, nonce=2)

        query = select(MultisigTransaction).where(
            MultisigTransaction.safe == shared_safe_tx.safe  # type: ignore
        )
        result = await db_session.execute(query)
        stored_tx = result.scalars().one()

        assert stored_tx.safe == shared_safe_tx.safe
        assert stored_tx.safe_tx_hash == shared_safe_tx.safe_tx_hash
        assert stored_tx.nonce == 1

    @db_session_context
    async def test_custom_field_coercion(self) -> None:
        safe_tx_hash = b"\x05" * 32
        max_uint_value = 2**256 - 1
        safe_address_hex = "0x" + "aa" * 20
        proposer_bytes = b"\x01" * 20
        delegate_bytes = b"\x02" * 20
        to_address_hex = "0x" + "bb" * 20
        gas_token_memory = memoryview(b"\x03" * 20)
        refund_receiver_memory = memoryview(b"\x04" * 20)
        origin = {"source": "coercion-test"}

        await multisig_transaction_factory(
            safe_tx_hash=safe_tx_hash,
            chain_id=99,
            safe=safe_address_hex,
            nonce=max_uint_value,
            proposer=proposer_bytes,
            proposed_by_delegate=delegate_bytes,
            tx_hash=b"\x06" * 32,
            to=to_address_hex,
            value=max_uint_value,
            operation=SafeOperationEnum.DELEGATE_CALL,
            safe_tx_gas=max_uint_value,
            base_gas=max_uint_value,
            gas_price=max_uint_value,
            gas_token=gas_token_memory,
            refund_receiver=refund_receiver_memory,
            failed=True,
            origin=origin,
        )

        # Remove cache
        db_session.expire_all()

        stored = await db_session.get(MultisigTransaction, safe_tx_hash)
        assert stored is not None

        assert stored.safe == bytes.fromhex(safe_address_hex[2:])
        assert stored.proposer == proposer_bytes
        assert stored.proposed_by_delegate == delegate_bytes
        assert stored.to == bytes.fromhex(to_address_hex[2:])
        assert stored.gas_token == bytes(gas_token_memory)
        assert stored.refund_receiver == bytes(refund_receiver_memory)
        assert stored.nonce == max_uint_value
        assert stored.value == max_uint_value
        assert stored.safe_tx_gas == max_uint_value
        assert stored.base_gas == max_uint_value
        assert stored.gas_price == max_uint_value
        assert stored.operation == SafeOperationEnum.DELEGATE_CALL
        assert stored.origin == origin
