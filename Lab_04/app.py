import random
import sys
import time
from collections.abc import Callable

from algorithms import (
    TreeNode,
    contains,
    fib,
    fib_iter,
    fib_naive,
    height,
    height_iter,
    nary_bfs,
    nary_dfs_iter,
    nary_postorder,
    nary_preorder,
    quicksort,
)


def seconds(func: Callable[[], object]) -> float:
    start = time.perf_counter()
    func()
    return time.perf_counter() - start


def random_tree(size: int, rng: random.Random) -> TreeNode:
    children: list[list[int]] = [[] for _ in range(size)]
    for child in range(1, size):
        children[rng.randrange(child)].append(child)
    nodes: dict[int, TreeNode] = {}
    for index in reversed(range(size)):
        nodes[index] = TreeNode(index, tuple(nodes[c] for c in children[index]))
    return nodes[0]


def chain(depth: int) -> TreeNode:
    node = TreeNode(depth)
    for value in reversed(range(1, depth)):
        node = TreeNode(value, (node,))
    return node


def main() -> None:
    print("quicksort:", quicksort([5, 3, 8, 3, 1, 9, 2]))

    tree = TreeNode(
        1,
        (
            TreeNode(2, (TreeNode(5), TreeNode(6))),
            TreeNode(3),
            TreeNode(4, (TreeNode(7),)),
        ),
    )
    print("preorder:", list(nary_preorder(tree)))
    print("postorder:", list(nary_postorder(tree)))
    print("dfs iter:", nary_dfs_iter(tree))
    print("bfs:", nary_bfs(tree))
    print("height:", height(tree), height_iter(tree))
    print("contains 7 / 10:", contains(tree, 7), contains(tree, 10))

    fib.cache_clear()
    print(f"fib(30) naive: {seconds(lambda: fib_naive(30)):.4f} s")
    print(f"fib(30) lru_cache: {seconds(lambda: fib(30)):.6f} s")
    print(f"fib(30) iter: {seconds(lambda: fib_iter(30)):.6f} s")
    print("cache_info:", fib.cache_info())

    big = random_tree(50_000, random.Random(14))
    print(f"height of random tree: {height(big)} = {height_iter(big)}")
    print(f"  recursive: {seconds(lambda: height(big)):.4f} s")
    print(f"  iterative: {seconds(lambda: height_iter(big)):.4f} s")

    deep = chain(5_000)
    print("recursion limit:", sys.getrecursionlimit())
    print("height_iter of chain 5000:", height_iter(deep))
    try:
        height(deep)
    except RecursionError:
        print("height of chain 5000: RecursionError")


if __name__ == "__main__":
    main()
