# This solves https://leetcode.com/problems/regular-expression-matching/

import typing as t
from collections import deque


class ExpectLiteral(t.NamedTuple):
    literal: str


class ExpectAnyChar(t.NamedTuple):
    pass


Expectation = t.Union[
    ExpectLiteral,
    ExpectAnyChar,
]


class TerminalNode(t.NamedTuple):
    pass


class TransitionNode(t.NamedTuple):
    expectation: Expectation
    next_node: 'DfaNode'  # type: ignore


class LoopNode(t.NamedTuple):
    expectation: Expectation
    next_node: 'DfaNode'  # type: ignore


DfaNode = t.Union[TerminalNode, TransitionNode, LoopNode]  # type: ignore


class MatcherState(t.NamedTuple):
    remainder: str
    dfa_node: DfaNode


def match_expectation(text: str, expectation: Expectation) -> t.Optional[str]:
    if isinstance(expectation, ExpectLiteral):
        literal = expectation.literal
        if text.startswith(literal):
            return text[len(literal):]
    elif isinstance(expectation, ExpectAnyChar):
        if text:
            return text[1:]
    return None


def advance(state: MatcherState) -> t.Iterable[MatcherState]:
    remainder, dfa_node = state
    if isinstance(dfa_node, TerminalNode):
        return ()
    updated_remainder = match_expectation(remainder, dfa_node.expectation)
    if isinstance(dfa_node, TransitionNode):
        if updated_remainder is not None:
            return (
                MatcherState(
                    updated_remainder,
                    dfa_node=dfa_node.next_node,
                ),
            )
        return ()
    if isinstance(dfa_node, LoopNode):
        if updated_remainder is not None:
            return (
                MatcherState(
                    remainder,
                    dfa_node=dfa_node.next_node,
                ),
                MatcherState(
                    updated_remainder,
                    dfa_node=dfa_node,
                ),
            )
        return (
            MatcherState(
                remainder,
                dfa_node=dfa_node.next_node,
            ),
        )
    return ()


def check_success(state: MatcherState) -> bool:
    return (
        isinstance(state.dfa_node, TerminalNode) and
        not state.remainder
    )


def match_dfa(text: str, initial: DfaNode) -> bool:
    if isinstance(initial, TerminalNode):
        return not text
    states = deque((
        MatcherState(
            remainder=text,
            dfa_node=initial,
        ),
    ))
    visited: t.Set[MatcherState] = set()
    while states:
        state = states.pop()
        if check_success(state):
            return True
        for next_state in advance(state):
            if next_state not in visited:
                states.append(next_state)
                visited.add(next_state)
    return False


def build_dfa(pattern: str) -> DfaNode:
    """Try to build dfa, traversing pattern in reverse"""
    result: DfaNode = TerminalNode()
    reversed_remaining = pattern[::-1]
    while reversed_remaining:
        head, star, tail = reversed_remaining.partition('*')
        if head:
            literals = head.split('.')
            while literals:
                first_literal, *literals = literals
                result = TransitionNode(
                    expectation=ExpectLiteral(first_literal[::-1]),
                    next_node=result,
                )
                if literals:
                    result = TransitionNode(
                        expectation=ExpectAnyChar(),
                        next_node=result,
                    )
        if star:
            if not tail:
                raise ValueError(f'Star proceeds nothing in pattern: {pattern}')
            repeated_char = tail[0]
            reversed_remaining = tail[1:]
            expectation: Expectation
            if repeated_char == '.':
                expectation = ExpectAnyChar()
            else:
                expectation = ExpectLiteral(repeated_char)
            result = LoopNode(
                expectation,
                next_node=result,
            )
        else:
            reversed_remaining = tail
    return result


def match(text: str, pattern: str) -> bool:
    return match_dfa(text, build_dfa(pattern))


class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        return match(s, p)


# Dfa for pattern abc.*d
test_dfa = TransitionNode(
    expectation=ExpectLiteral('abc'),
    next_node=LoopNode(
        expectation=ExpectAnyChar(),
        next_node=TransitionNode(
            expectation=ExpectLiteral('d'),
            next_node=TerminalNode(),
        ),
    ),
)


def test_match_dfa() -> None:
    assert match_dfa('abcd', test_dfa)
    assert match_dfa('abc1d', test_dfa)
    assert match_dfa('abc12d', test_dfa)
    assert match_dfa('abc123d', test_dfa)
    assert not match_dfa('abc', test_dfa)
    assert not match_dfa('d', test_dfa)
    assert not match_dfa('abc123de', test_dfa)


def test_build_dfa() -> None:
    assert build_dfa('abc.*d') == test_dfa


def test_match() -> None:
    assert match('abc12345d', 'abc.*d')
    assert match('', '')
    assert match('aaaaaaaaaaaaab', 'a*a*a*a*a*a*a*a*a*a*a*a*b')
    assert not match('aaaaaaaaaaaaab', 'a*a*a*a*a*a*a*a*a*a*a*a*c')


if __name__ == '__main__':
    test_match_dfa()
    test_build_dfa()
    test_match()
