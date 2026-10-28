"""Small offline Python / C++ highlighters; preserve original text exactly."""
from __future__ import annotations

import html
import io
import keyword
import re
import token
import tokenize


def _span(kind, text):
    escaped = html.escape(text)
    return f'<span class="syntax-{kind}">{escaped}</span>' if kind else escaped


def python_html(source):
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    def position(point):
        line, column = point
        return min(len(source), offsets[min(line - 1, len(offsets) - 1)] + column)

    parts, cursor, expect_definition = [], 0, False
    try:
        for item in tokenize.generate_tokens(io.StringIO(source).readline):
            start, end = position(item.start), position(item.end)
            if start < cursor or end <= start:
                continue
            parts.append(html.escape(source[cursor:start]))
            kind = {token.STRING: "string", token.NUMBER: "number", tokenize.COMMENT: "comment"}.get(item.type)
            if item.type == token.NAME:
                if keyword.iskeyword(item.string):
                    kind = "keyword"
                elif expect_definition:
                    kind = "function"
                elif item.string in {"True", "False", "None", "int", "float", "str", "range", "len", "min", "max", "bool", "tuple", "list", "dict", "print"}:
                    kind = "builtin"
                expect_definition = item.string in {"def", "class"}
            parts.append(_span(kind, source[start:end]))
            cursor = end
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass  # A truncated dump remains viewable and copyable.
    parts.append(html.escape(source[cursor:]))
    return "".join(parts)


_CPP = re.compile(
    r'(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|'
    r'(?P<string>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|'
    r'(?P<directive>\#[ \t]*[a-zA-Z_]\w*)|'
    r'(?P<number>\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)[uUlLfF]*\b)|'
    r'(?P<name>[a-zA-Z_]\w*)'
)
_KEYWORDS = set("alignas alignof asm auto bool break case catch char class const constexpr continue decltype default delete do double else enum explicit extern false float for friend goto if inline int long namespace new noexcept nullptr operator private protected public register reinterpret_cast return short signed sizeof static static_cast struct switch template this thread_local throw true try typedef typename union unsigned using virtual void volatile while __global__ __device__ __host__ __aicore__ __gm__ __ubuf__ __cbuf__ __restrict__".split())


def cpp_html(source):
    parts, cursor = [], 0
    for match in _CPP.finditer(source):
        parts.append(html.escape(source[cursor:match.start()]))
        kind = match.lastgroup
        if kind == "name":
            word = match.group()
            kind = "keyword" if word in _KEYWORDS else "builtin" if re.fullmatch(r"(?:u?int\d+_t|half|bfloat16_t|float\d+|vector|memref)", word) else "function" if re.match(r"\s*\(", source[match.end():]) else None
        parts.append(_span(kind, match.group()))
        cursor = match.end()
    parts.append(html.escape(source[cursor:]))
    return "".join(parts)
