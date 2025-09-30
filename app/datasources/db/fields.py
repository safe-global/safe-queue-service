from __future__ import annotations

from sqlalchemy import Numeric
from sqlalchemy.types import BINARY, TypeDecorator

# Max value for Ethereum numeric fields
UINT256_MAX = 2**256 - 1


class Uint256Type(TypeDecorator[int]):
    """Store uint256 values in a numeric column while enforcing bounds."""

    impl = Numeric
    cache_ok = True

    def __init__(self) -> None:
        super().__init__(precision=78, scale=0, asdecimal=False)

    def process_bind_param(self, value, dialect) -> None | int:
        if value is None:
            return value
        if not isinstance(value, int):
            raise TypeError("Uint256Type expects Python int values")
        if value < 0 or value > UINT256_MAX:
            raise ValueError("Uint256Type value out of range")
        return value

    def process_result_value(self, value, dialect) -> None | int:
        if value is None:
            return None
        return int(value)


class EthereumAddressType(TypeDecorator[bytes]):
    """Persist Ethereum addresses as 20-byte binaries accepting multiple input formats."""

    impl = BINARY(20)
    cache_ok = True

    def process_bind_param(
        self, value: None | str | memoryview | bytes, dialect
    ) -> None | bytes:
        if value is None:
            return None
        return self._coerce_to_bytes(value)

    def process_result_value(
        self, value: None | memoryview | bytes, dialect
    ) -> None | bytes:
        if value is None:
            return None
        if not isinstance(value, (memoryview, bytes)):
            raise TypeError(
                "EthereumAddressType expects memoryview/bytes from the database"
            )
        value = bytes(value)
        if len(value) != 20:
            raise ValueError(
                "EthereumAddressType expects 20-byte values from the database"
            )
        return value

    @staticmethod
    def _coerce_to_bytes(value: str | memoryview | bytes) -> bytes:
        if isinstance(value, (memoryview, bytes)):
            raw = bytes(value)
            if len(raw) != 20:
                raise ValueError("EthereumAddressType expects 20-byte values")
            return raw

        if isinstance(value, str):
            text = value.strip()
            if text.startswith("0x") or text.startswith("0X"):
                text = text[2:]

            try:
                return bytes.fromhex(text)
            except ValueError as exc:
                raise ValueError("Invalid Ethereum address format") from exc

        raise TypeError("EthereumAddressType expects bytes or hex string inputs")
