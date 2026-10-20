"""JSON persistence for the library."""
import json
from pathlib import Path

from .library import Library
from .models import Book, Loan, Member


def save(library: Library, path: str) -> None:
    data = {
        "books": [b.to_dict() for b in library.books.values()],
        "members": [m.to_dict() for m in library.members.values()],
        "loans": [l.to_dict() for l in library.loans],
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load(path: str) -> Library:
    library = Library()
    file = Path(path)
    if not file.exists():
        return library
    data = json.loads(file.read_text(encoding="utf-8"))
    for b in data.get("books", []):
        library.add_book(Book.from_dict(b))
    for m in data.get("members", []):
        library.add_member(Member.from_dict(m))
    library.loans = [Loan.from_dict(l) for l in data.get("loans", [])]
    return library
