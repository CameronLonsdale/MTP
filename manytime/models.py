"""
Models module
"""

from typing import Optional


class Key:
    """
    A key used for decrypting OTP
    supports partial decryption
    """
    def __init__(self, key: bytearray, unknown_character: str = '_'):
        self.key = key
        self.unknown_character = unknown_character

    def __str__(self) -> str:
        """A string representation of a key is a hex digest"""
        # Display two unknown characters because each key byte is represented by two hex digits
        return ''.join(format(k, '02x') if k is not None else 2 * self.unknown_character for k in self.key)

    def __iter__(self) -> iter:
        """Iterator wrapper over key"""
        return iter(self.key)

    def __getitem__(self, index: int) -> Optional[str]:
        """Getter wrapper"""
        return self.key[index]

    def __setitem__(self, index: int, value: Optional[str]) -> None:
        """Setter wrapper"""
        self.key[index] = value
