from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .data import Record
from .exceptions import ReportOutputError
from .processing import summarize


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _pdf_document(lines: list[str]) -> bytes:
    """Create a small valid PDF using only the PDF standard and Helvetica."""
    pages = [lines[i:i + 48] for i in range(0, len(lines), 48)] or [[]]
    font_id = 3 + len(pages) * 2
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        font_id: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    page_ids = []

    for index, page_lines in enumerate(pages):
        page_id = 3 + index * 2
        content_id = page_id + 1
        page_ids.append(page_id)
        commands = ["BT", "/F1 10 Tf", "50 760 Td", "14 TL"]
        for line in page_lines:
            commands.append(f"({_escape(line[:115])}) Tj")
            commands.append("T*")
        commands.append("ET")
        content = "\n".join(commands).encode("latin-1", "replace")
        objects[content_id] = (
            f"<< /Length {len(content)} >>\nstream\n".encode()
            + content
            + b"\nendstream"
        )
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode()

    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()

    max_id = font_id
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0] * (max_id + 1)

    for obj_id in range(1, max_id + 1):
        offsets[obj_id] = len(output)
        output.extend(f"{obj_id} 0 obj\n".encode())
        output.extend(objects[obj_id])
        output.extend(b"\nendobj\n")

    xref = len(output)
    output.extend(f"xref\n0 {max_id + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for obj_id in range(1, max_id + 1):
        output.extend(f"{offsets[obj_id]:010d} 00000 n \n".encode())
    output.extend(
        f"trailer\n<< /Size {max_id + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(output)


def create_pdf(records: list[Record], output: str, title: str = "Automated Enterprise Report") -> None:
    summary = summarize(records)
    lines = [
        title,
        "=" * 70,
        "Automated Python Capstone Report",
        "",
        f"Records: {summary['record_count']}",
        f"Total amount: {summary['total_amount']:.2f}",
        f"Average amount: {summary['average_amount']:.2f}",
        f"Minimum amount: {summary['minimum_amount']:.2f}",
        f"Maximum amount: {summary['maximum_amount']:.2f}",
        "",
        "Status distribution",
        "-" * 70,
    ]
    lines.extend(f"{key}: {value}" for key, value in summary["status_counts"].items())
    lines += ["", "Category totals", "-" * 70]
    lines.extend(f"{key}: {value:.2f}" for key, value in summary["category_totals"].items())
    lines += ["", "Detailed records", "-" * 70]
    lines.append("ID | Customer | Category | Amount | Status")
    for record in records:
        lines.append(
            f"{record.id} | {record.customer} | {record.category} | "
            f"{record.amount:.2f} | {record.status}"
        )

    try:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_suffix(target.suffix + ".tmp")
        temp.write_bytes(_pdf_document(lines))
        temp.replace(target)
    except OSError as exc:
        raise ReportOutputError(f"could not write PDF: {exc}") from exc
