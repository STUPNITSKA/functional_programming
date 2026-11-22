from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache
from random import choice
from typing import Optional


def quicksort(xs: list[int]) -> list[int]:
    if len(xs) <= 1:
        return xs[:]
    pivot = choice(xs)
    left = [x for x in xs if x < pivot]
    mid = [x for x in xs if x == pivot]
    right = [x for x in xs if x > pivot]
    return quicksort(left) + mid + quicksort(right)


@dataclass(slots=True)
class Node:
    key: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None


def preorder(t: Node | None) -> Iterator[int]:
    if t is None:
        return
    yield t.key
    yield from preorder(t.left)
    yield from preorder(t.right)


def inorder(t: Node | None) -> Iterator[int]:
    if t is None:
        return
    yield from inorder(t.left)
    yield t.key
    yield from inorder(t.right)


def postorder(t: Node | None) -> Iterator[int]:
    if t is None:
        return
    yield from postorder(t.left)
    yield from postorder(t.right)
    yield t.key


def bfs_level_order(t: Node | None) -> list[int]:
    if t is None:
        return []
    queue, out = deque([t]), []
    while queue:
        node = queue.popleft()
        out.append(node.key)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return out


def dfs_preorder_iter(t: Node | None) -> list[int]:
    if t is None:
        return []
    stack, out = [t], []
    while stack:
        node = stack.pop()
        out.append(node.key)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return out


def _check_n(n: int) -> None:
    if n < 0:
        raise ValueError("n must be non-negative")


@lru_cache(maxsize=None)
def fib(n: int) -> int:
    _check_n(n)
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_naive(n: int) -> int:
    _check_n(n)
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_iter(n: int) -> int:
    _check_n(n)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@dataclass(frozen=True, slots=True)
class TreeNode:
    value: int
    children: tuple["TreeNode", ...] = ()


def nary_preorder(t: TreeNode | None) -> Iterator[int]:
    if t is None:
        return
    yield t.value
    for child in t.children:
        yield from nary_preorder(child)


def nary_postorder(t: TreeNode | None) -> Iterator[int]:
    if t is None:
        return
    for child in t.children:
        yield from nary_postorder(child)
    yield t.value


def contains(t: TreeNode | None, value: int) -> bool:
    if t is None:
        return False
    if t.value == value:
        return True
    return any(contains(child, value) for child in t.children)


def nary_dfs_iter(t: TreeNode | None) -> list[int]:
    if t is None:
        return []
    stack, out = [t], []
    while stack:
        node = stack.pop()
        out.append(node.value)
        stack.extend(reversed(node.children))
    return out


def nary_bfs(t: TreeNode | None) -> list[int]:
    if t is None:
        return []
    queue, out = deque([t]), []
    while queue:
        node = queue.popleft()
        out.append(node.value)
        queue.extend(node.children)
    return out


def height(t: TreeNode | None) -> int:
    if t is None:
        return 0
    return 1 + max((height(child) for child in t.children), default=0)


def height_iter(t: TreeNode | None) -> int:
    if t is None:
        return 0
    level, result = [t], 0
    while level:
        result += 1
        level = [child for node in level for child in node.children]
    return result
