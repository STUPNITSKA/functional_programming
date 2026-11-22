import pytest

from algorithms import (
    Node,
    TreeNode,
    bfs_level_order,
    contains,
    dfs_preorder_iter,
    height,
    height_iter,
    inorder,
    nary_bfs,
    nary_dfs_iter,
    nary_postorder,
    nary_preorder,
    postorder,
    preorder,
)


def sample_tree() -> Node:
    #      4
    #     / \
    #    2   6
    #   / \   \
    #  1   3   7
    return Node(4, left=Node(2, Node(1), Node(3)), right=Node(6, None, Node(7)))


def sample_nary() -> TreeNode:
    #        1
    #     /  |  \
    #    2   3   4
    #   / \      |
    #  5   6     7
    return TreeNode(
        1,
        (
            TreeNode(2, (TreeNode(5), TreeNode(6))),
            TreeNode(3),
            TreeNode(4, (TreeNode(7),)),
        ),
    )


def chain(depth: int) -> TreeNode:
    node = TreeNode(depth)
    for value in reversed(range(1, depth)):
        node = TreeNode(value, (node,))
    return node


def test_traversals() -> None:
    t = sample_tree()
    assert list(preorder(t)) == [4, 2, 1, 3, 6, 7]
    assert list(inorder(t)) == [1, 2, 3, 4, 6, 7]
    assert list(postorder(t)) == [1, 3, 2, 7, 6, 4]
    assert bfs_level_order(t) == [4, 2, 6, 1, 3, 7]
    assert dfs_preorder_iter(t) == [4, 2, 1, 3, 6, 7]


def test_binary_empty_tree() -> None:
    assert list(preorder(None)) == []
    assert list(inorder(None)) == []
    assert list(postorder(None)) == []
    assert bfs_level_order(None) == []
    assert dfs_preorder_iter(None) == []


def test_nary_traversals() -> None:
    t = sample_nary()
    assert list(nary_preorder(t)) == [1, 2, 5, 6, 3, 4, 7]
    assert list(nary_postorder(t)) == [5, 6, 2, 3, 7, 4, 1]
    assert nary_dfs_iter(t) == list(nary_preorder(t))
    assert nary_bfs(t) == [1, 2, 3, 4, 5, 6, 7]


def test_nary_empty_and_single() -> None:
    assert list(nary_preorder(None)) == []
    assert nary_bfs(None) == []
    assert nary_dfs_iter(TreeNode(9)) == [9]
    assert list(nary_postorder(TreeNode(9))) == [9]


@pytest.mark.parametrize(
    ("value", "expected"), [(1, True), (7, True), (3, True), (8, False)]
)
def test_contains(value: int, expected: bool) -> None:
    assert contains(sample_nary(), value) is expected


def test_contains_empty() -> None:
    assert contains(None, 1) is False


def test_height() -> None:
    assert height(None) == height_iter(None) == 0
    assert height(TreeNode(1)) == height_iter(TreeNode(1)) == 1
    assert height(sample_nary()) == height_iter(sample_nary()) == 3
    assert height(chain(50)) == height_iter(chain(50)) == 50


def test_tree_is_not_changed() -> None:
    t = sample_nary()
    list(nary_preorder(t))
    nary_dfs_iter(t)
    nary_bfs(t)
    height(t)
    assert t == sample_nary()


def test_deep_tree_needs_iterative_height() -> None:
    deep = chain(5_000)
    assert height_iter(deep) == 5_000
    assert nary_dfs_iter(deep)[-1] == 5_000
    with pytest.raises(RecursionError):
        height(deep)
