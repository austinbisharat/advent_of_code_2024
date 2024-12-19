import dataclasses
from typing import Iterable


class Trie:
    @dataclasses.dataclass
    class _TrieNode:
        char: str
        is_terminal: bool
        children: dict[str, 'Trie._TrieNode'] = dataclasses.field(default_factory=dict)

        def is_leaf(self) -> bool:
            return not self.children

    def __init__(self):
        self.root = Trie._TrieNode('', False)

    def insert(self, word: str) -> None:
        current = self.root
        for char in word:
            current = current.children.setdefault(char, Trie._TrieNode(char, False))
        current.is_terminal = True

    def has_prefix(self, prefix: str) -> bool:
        current = self.root
        for char in prefix:
            if char not in current.children:
                return False
            current = current.children[char]
        return True

    def has_word(self, word: str) -> bool:
        current = self.root
        for char in word:
            if char not in current.children:
                return False
            current = current.children[char]
        return current.is_terminal

    def get_longest_matching_word(self, word: str) -> str:
        current = self.root
        longest_match_len = 0
        for i, char in enumerate(word):
            current = current.children[char]
            if current.is_terminal:
                longest_match_len = max(longest_match_len, i + 1)
        return word[0:longest_match_len]

    def get_longest_matching_prefix(self, word: str) -> str:
        current = self.root
        for i, char in enumerate(word):
            if char not in current.children:
                return word[0:i]
            current = current.children[char]
        return word

    def iter_all_matching_prefixes(self, word: str) -> Iterable[str]:
        current = self.root
        for i, char in enumerate(word):
            if char not in current.children:
                break
            yield word[0:i + 1]
            current = current.children[char]

    def iter_all_matching_words(self, word: str) -> Iterable[str]:
        current = self.root
        for i, char in enumerate(word):
            if char not in current.children:
                break
            current = current.children[char]
            if current.is_terminal:
                yield word[0:i + 1]
