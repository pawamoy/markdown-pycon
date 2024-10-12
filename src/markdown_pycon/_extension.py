"""This module contains the Markdown block processor and extension."""

from __future__ import annotations

import re
import textwrap
from re import Pattern
from typing import TYPE_CHECKING, Any

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.extensions.codehilite import CodeHiliteExtension
from markupsafe import Markup
from pymdownx.highlight import Highlight, HighlightExtension

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from markdown import Markdown

_RE_DOCTEST_FLAGS: Pattern = re.compile(r"(\s*#\s*doctest:.+)$", re.MULTILINE)
_RE_DOCTEST_BLANKLINE: Pattern = re.compile(r"^\s*<BLANKLINE>\s*$", re.MULTILINE)


class Highlighter(Highlight):
    """Code highlighter that tries to match the Markdown configuration.

    Picking up the global config and defaults works only if you use the `codehilite` or
    `pymdownx.highlight` (recommended) Markdown extension.

    -   If you use `pymdownx.highlight`, highlighting settings are picked up from it, and the
        default CSS class is `.highlight`. This also means the default of `guess_lang: false`.

    -   Otherwise, if you use the `codehilite` extension, settings are picked up from it, and the
        default CSS class is `.codehilite`. Also consider setting `guess_lang: false`.

    -   If neither are added to `markdown_extensions`, highlighting is enabled anyway. This is for
        backwards compatibility. If you really want to disable highlighting even in *mkdocstrings*,
        add one of these extensions anyway and set `use_pygments: false`.

    The underlying implementation is `pymdownx.highlight` regardless.
    """

    # https://raw.githubusercontent.com/facelessuser/pymdown-extensions/main/docs/src/markdown/extensions/highlight.md
    _highlight_config_keys = frozenset(
        (
            "css_class",
            "guess_lang",
            "pygments_style",
            "noclasses",
            "use_pygments",
            "linenums",
            "linenums_special",
            "linenums_style",
            "linenums_class",
            "extend_pygments_lang",
            "language_prefix",
            "code_attr_on_pre",
            "auto_title",
            "auto_title_map",
            "line_spans",
            "anchor_linenums",
            "line_anchors",
        ),
    )

    def __init__(self, md: Markdown):
        """Configure to match a `markdown.Markdown` instance.

        Arguments:
            md: The Markdown instance to read configs from.
        """
        config: dict[str, Any] = {}
        self._highlighter: str | None = None
        for ext in md.registeredExtensions:
            if isinstance(ext, HighlightExtension) and (ext.enabled or not config):
                self._highlighter = "highlight"
                config = ext.getConfigs()
                break  # This one takes priority, no need to continue looking
            if isinstance(ext, CodeHiliteExtension) and not config:
                self._highlighter = "codehilite"
                config = ext.getConfigs()
                config["language_prefix"] = config["lang_prefix"]
        self._css_class = config.pop("css_class", "highlight")
        super().__init__(**{name: opt for name, opt in config.items() if name in self._highlight_config_keys})

    def highlight(
        self,
        src: str,
        language: str | None = None,
        *,
        inline: bool = False,
        dedent: bool = True,
        linenums: bool | None = None,
        **kwargs: Any,
    ) -> str:
        """Highlight a code-snippet.

        Arguments:
            src: The code to highlight.
            language: Explicitly tell what language to use for highlighting.
            inline: Whether to highlight as inline.
            dedent: Whether to dedent the code before highlighting it or not.
            linenums: Whether to add line numbers in the result.
            **kwargs: Pass on to `pymdownx.highlight.Highlight.highlight`.

        Returns:
            The highlighted code as HTML text, marked safe (not escaped for HTML).
        """
        if isinstance(src, Markup):
            src = src.unescape()
        if dedent:
            src = textwrap.dedent(src)

        kwargs.setdefault("css_class", self._css_class)
        old_linenums = self.linenums  # type: ignore[has-type]
        if linenums is not None:
            self.linenums = linenums
        try:
            result = super().highlight(src, language, inline=inline, **kwargs)
        finally:
            self.linenums = old_linenums

        if inline:
            # From the maintainer of codehilite, the codehilite CSS class, as defined by the user,
            # should never be added to inline code, because codehilite does not support inline code.
            # See https://github.com/Python-Markdown/markdown/issues/1220#issuecomment-1692160297.
            css_class = "" if self._highlighter == "codehilite" else kwargs["css_class"]
            return Markup(f'<code class="{css_class} language-{language}">{result.text}</code>')
        return Markup(result)


class PyConBlockProcessor(BlockProcessor):
    """Our block processor."""

    def test(self, parent: Element, block: str) -> bool:  # noqa: ARG002
        return block.startswith(">>>")

    def run(self, parent: Element, blocks: list[str]) -> bool | None:  # noqa: ARG002
        block = blocks.pop(0)
        block = _RE_DOCTEST_FLAGS.sub("", block)
        block = _RE_DOCTEST_BLANKLINE.sub("", block)
        blocks.insert(0, Highlighter(self.parser.md).highlight(block, "pycon"))
        return None


class PyConExtension(Extension):
    """Our Markdown extension."""

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
        """Register the block processor.

        Add an instance of our [`PyConBlockProcessor`][markdown_pycon.PyConBlockProcessor] to the Markdown parser.

        Parameters:
            md: A Markdown instance.
        """
        md.parser.blockprocessors.register(PyConBlockProcessor(md.parser), "pycon", priority=30)


def makeExtension(*args: Any, **kwargs: Any) -> PyConExtension:  # noqa: N802
    """Return extension."""
    return PyConExtension(*args, **kwargs)
