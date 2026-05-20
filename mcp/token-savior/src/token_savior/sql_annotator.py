"""SQL / dbt annotator for token-savior.

Extracts structural metadata from .sql files:
- CTEs as FunctionInfo (name, line range, parameters=[columns referenced])
- dbt ref()/source() calls as ImportInfo
- dbt config() blocks
- Jinja macros as FunctionInfo
- Dependency graph: CTE → CTEs/refs it references
"""

import re
from token_savior.models import (
    FunctionInfo,
    ImportInfo,
    LineRange,
    StructuralMetadata,
)

# --- Patterns ----------------------------------------------------------------

# dbt ref('model') or ref('project', 'model')
_REF_PATTERN = re.compile(
    r"""\{\{\s*ref\(\s*['"]([^'"]+)['"]\s*(?:,\s*['"]([^'"]+)['"]\s*)?\)\s*\}\}""",
)

# dbt source('source_name', 'table_name')
_SOURCE_PATTERN = re.compile(
    r"""\{\{\s*source\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]\s*\)\s*\}\}""",
)

# dbt config(...) block — capture the full config content
_CONFIG_PATTERN = re.compile(
    r"""\{\{\s*config\(\s*(.*?)\s*\)\s*\}\}""",
    re.DOTALL,
)

# CTE definitions: <name> AS (
_CTE_PATTERN = re.compile(
    r"""(?:^|,)\s*(\w+)\s+AS\s*\(""",
    re.IGNORECASE | re.MULTILINE,
)

# WITH keyword (start of CTE chain)
_WITH_PATTERN = re.compile(r"""^\s*WITH\b""", re.IGNORECASE | re.MULTILINE)

# Jinja macro: {% macro name(args) %}
_MACRO_PATTERN = re.compile(
    r"""\{%[-\s]*macro\s+(\w+)\s*\(([^)]*)\)\s*[-]?%\}""",
)

# Jinja endmacro
_ENDMACRO_PATTERN = re.compile(r"""\{%[-\s]*endmacro\s*[-]?%\}""")

# Final select (after last CTE)
_FINAL_SELECT_PATTERN = re.compile(
    r"""\)\s*(?:,\s*\w+\s+AS\s*\(.*?\)\s*)*SELECT\b""",
    re.IGNORECASE | re.DOTALL,
)


def _compute_line_offsets(source: str) -> tuple[list[str], list[int]]:
    """Split source into lines and compute character offsets."""
    lines = source.splitlines(keepends=False)
    offsets: list[int] = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line) + 1  # +1 for newline
    return lines, offsets


def _line_at_offset(offsets: list[int], char_offset: int) -> int:
    """Convert a character offset to a 1-indexed line number."""
    for i, off in enumerate(offsets):
        if i + 1 < len(offsets) and offsets[i + 1] > char_offset:
            return i + 1
        if i + 1 == len(offsets):
            return i + 1
    return 1


def _find_matching_paren(source: str, start: int) -> int:
    """Find the closing paren matching the open paren at start."""
    depth = 0
    i = start
    in_string: str | None = None
    while i < len(source):
        ch = source[i]
        if in_string:
            if ch == in_string and (i == 0 or source[i - 1] != "\\"):
                in_string = None
        elif ch in ("'", '"'):
            in_string = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(source) - 1


def _extract_ctes(
    source: str, lines: list[str], offsets: list[int]
) -> list[FunctionInfo]:
    """Extract CTE definitions as FunctionInfo entries."""
    ctes: list[FunctionInfo] = []

    with_match = _WITH_PATTERN.search(source)
    if not with_match:
        return ctes

    # Find all CTE names and their positions
    for match in _CTE_PATTERN.finditer(source, with_match.start()):
        name = match.group(1).strip()
        # Skip SQL keywords that might false-match
        if name.upper() in ("SELECT", "INSERT", "UPDATE", "DELETE", "FROM", "WHERE",
                            "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "CROSS",
                            "GROUP", "ORDER", "HAVING", "LIMIT", "UNION", "EXCEPT",
                            "INTERSECT", "VALUES", "SET", "INTO", "CREATE", "DROP",
                            "ALTER", "TABLE", "VIEW", "INDEX", "NOT", "NULL", "AND",
                            "OR", "IN", "ON", "AS", "BY", "ALL", "ANY", "CASE",
                            "WHEN", "THEN", "ELSE", "END", "EXISTS", "BETWEEN"):
            continue

        # Find the opening paren after AS
        paren_start = source.find("(", match.end() - 1)
        if paren_start < 0:
            continue

        paren_end = _find_matching_paren(source, paren_start)
        start_line = _line_at_offset(offsets, match.start())
        end_line = _line_at_offset(offsets, paren_end)

        ctes.append(FunctionInfo(
            name=name,
            qualified_name=name,
            line_range=LineRange(start=start_line, end=end_line),
            parameters=[],
            decorators=["cte"],
            docstring=None,
            is_method=False,
            parent_class=None,
        ))

    return ctes


def _extract_macros(
    source: str, lines: list[str], offsets: list[int]
) -> list[FunctionInfo]:
    """Extract Jinja macro definitions as FunctionInfo entries."""
    macros: list[FunctionInfo] = []

    for match in _MACRO_PATTERN.finditer(source):
        name = match.group(1)
        params_str = match.group(2).strip()
        params = [p.strip().split("=")[0].strip()
                  for p in params_str.split(",") if p.strip()] if params_str else []

        start_line = _line_at_offset(offsets, match.start())

        # Find the matching endmacro
        endmacro = _ENDMACRO_PATTERN.search(source, match.end())
        end_line = _line_at_offset(offsets, endmacro.start()) if endmacro else start_line

        macros.append(FunctionInfo(
            name=name,
            qualified_name=name,
            line_range=LineRange(start=start_line, end=end_line),
            parameters=params,
            decorators=["macro"],
            docstring=None,
            is_method=False,
            parent_class=None,
        ))

    return macros


def _extract_imports(
    source: str, offsets: list[int]
) -> list[ImportInfo]:
    """Extract dbt ref() and source() calls as ImportInfo entries."""
    imports: list[ImportInfo] = []

    for match in _REF_PATTERN.finditer(source):
        project = match.group(1)
        model = match.group(2)
        line_num = _line_at_offset(offsets, match.start())

        if model:
            # Cross-project ref: ref('project', 'model')
            imports.append(ImportInfo(
                module=project,
                names=[model],
                alias=None,
                line_number=line_num,
                is_from_import=True,
            ))
        else:
            # Local ref: ref('model')
            imports.append(ImportInfo(
                module=project,
                names=[],
                alias=None,
                line_number=line_num,
                is_from_import=False,
            ))

    for match in _SOURCE_PATTERN.finditer(source):
        source_name = match.group(1)
        table_name = match.group(2)
        line_num = _line_at_offset(offsets, match.start())

        imports.append(ImportInfo(
            module=f"source.{source_name}",
            names=[table_name],
            alias=None,
            line_number=line_num,
            is_from_import=True,
        ))

    return imports


def _build_dependency_graph(
    ctes: list[FunctionInfo],
    macros: list[FunctionInfo],
    imports: list[ImportInfo],
    source: str,
) -> dict[str, list[str]]:
    """Build intra-file dependency graph.

    Maps each CTE/macro name to the CTEs and ref'd models it references.
    """
    graph: dict[str, list[str]] = {}
    all_names = {c.name for c in ctes} | {m.name for m in macros}
    ref_names = {imp.module for imp in imports if not imp.is_from_import}

    for func in [*ctes, *macros]:
        start = 0
        end = len(source)
        # Narrow to the function's body range if possible
        if func.line_range.start > 0:
            lines = source.splitlines(keepends=True)
            body_start = sum(len(lines[i]) for i in range(func.line_range.start - 1))
            body_end = sum(len(lines[i]) for i in range(func.line_range.end))
            start = body_start
            end = min(body_end, len(source))

        body = source[start:end]
        deps: list[str] = []

        for name in all_names | ref_names:
            if name == func.name:
                continue
            if re.search(r"\b" + re.escape(name) + r"\b", body):
                deps.append(name)

        if deps:
            graph[func.name] = sorted(deps)

    return graph


def annotate_sql(source: str, source_name: str = "<source>") -> StructuralMetadata:
    """Annotate a SQL/dbt file with structural metadata."""
    lines, offsets = _compute_line_offsets(source)

    ctes = _extract_ctes(source, lines, offsets)
    macros = _extract_macros(source, lines, offsets)
    imports = _extract_imports(source, offsets)
    dep_graph = _build_dependency_graph(ctes, macros, imports, source)

    return StructuralMetadata(
        source_name=source_name,
        total_lines=len(lines),
        total_chars=len(source),
        lines=lines,
        line_char_offsets=offsets,
        functions=[*ctes, *macros],
        classes=[],
        imports=imports,
        sections=[],
        dependency_graph=dep_graph,
    )
