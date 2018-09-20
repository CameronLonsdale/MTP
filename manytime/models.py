"""
Models module
"""

from typing import Optional


class Key:
    """
    A key used for decrypting OTP
    supports partial decryption
    """
    def __init__(self, key: bytearray, unknown_character: tuple = ('unknown', '_')):
        self.key = key
        self.unknown_character = unknown_character

    def to_text(self):
        # Using two unknown characters in this way in order to not merge two tuples
        return [format(k, '02x') if k is not None else [self.unknown_character, self.unknown_character] for k in self.key]

    def __iter__(self) -> iter:
        """Iterator wrapper over key"""
        return iter(self.key)

    def __getitem__(self, index: int) -> Optional[str]:
        """Getter wrapper"""
        return self.key[index]

    def __setitem__(self, index: int, value: Optional[str]) -> None:
        """Setter wrapper"""
        self.key[index] = value
