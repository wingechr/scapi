class CodeBlock:
    """lines of code in same indentation"""

    def __init__(self, *parts):
        """
        Args:
            *parts: lines of code (also multilines), code blocks, or None (empty line)
        """
        self.parts = []
        if parts:
            self += parts

    def __add__(self, it):
        if it is None:
            self.parts.append(None)
        elif isinstance(it, (list, tuple)):
            for i in it:
                self += i
        elif isinstance(it, CodeBlock):
            self.parts.append(it)
        else:
            for line in str(it).splitlines(keepends=False):
                self.parts.append(line.strip())
        return self

    def lines(self):
        """iterate over lines, adding indentation"""
        for p in self.parts:
            if not p:
                yield ""
            elif isinstance(p, str):
                yield p
            else:  # Codeblock
                yield from p.lines()

    def __str__(self):
        return "\n".join(self.lines())


class IndentedCodeBlock(CodeBlock):
    """all lines except header (and footer, if exist) are indented"""

    def __init__(self, header, *parts, footer=None):
        super().__init__(*parts)
        self.header = CodeBlock(header)
        self.footer = CodeBlock(footer) if footer else None

    def lines(self):
        yield from self.header.lines()
        for line in super().lines():
            yield "    " + line
        if self.footer:
            yield from self.footer.lines()


class CommaJoinedCodeBlock(CodeBlock):
    def __init__(self, *parts, join_on=","):
        super().__init__(*parts)
        self.join_on = join_on

    def lines(self):
        lines = list(super().lines())
        for i, line in enumerate(lines):
            if i + 1 == len(lines):  # last line
                yield line
            else:
                yield line + self.join_on
