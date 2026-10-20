"""Command-line menu for the library system."""
import shutil
from pathlib import Path

from .exceptions import LibraryError
from .models import Book, Student, Teacher
from . import storage

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_data.json"

MENU = """
===== Library Management System =====
1. List all books
2. Search books
3. Add book
4. Add member
5. Borrow book
6. Return book
7. Show overdue loans
8. Save and exit
"""


def run(data_path: str) -> None:
    # First run: start from the bundled sample data.
    if not Path(data_path).exists() and SAMPLE_PATH.exists():
        Path(data_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SAMPLE_PATH, data_path)
    library = storage.load(data_path)
    print(f"Loaded {len(library.books)} books and {len(library.members)} members.")
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                for book in library.books.values():
                    print(" -", book)
            elif choice == "2":
                results = library.search_books(input("Search term: "))
                print("\n".join(f" - {b}" for b in results) or "No matches.")
            elif choice == "3":
                library.add_book(Book(
                    isbn=input("ISBN: ").strip(), title=input("Title: ").strip(),
                    author=input("Author: ").strip(), year=int(input("Year: ")),
                    copies=int(input("Copies: "))))
                print("Book added.")
            elif choice == "4":
                kind = input("Type (student/teacher): ").strip().lower()
                cls = {"student": Student, "teacher": Teacher}.get(kind)
                if cls is None:
                    print("Unknown type.")
                    continue
                library.add_member(cls(input("Member ID: ").strip(),
                                       input("Name: ").strip(),
                                       input("Email: ").strip()))
                print("Member added.")
            elif choice == "5":
                loan = library.borrow(input("ISBN: ").strip(), input("Member ID: ").strip())
                print(f"Issued. Due on {loan.due_date}.")
            elif choice == "6":
                fine = library.return_book(input("ISBN: ").strip(), input("Member ID: ").strip())
                print("Returned." + (f" Fine due: {fine}" if fine else " No fine."))
            elif choice == "7":
                overdue = library.overdue_loans()
                for l in overdue:
                    print(f" - {l.isbn} | member {l.member_id} | due {l.due_date}")
                if not overdue:
                    print("No overdue loans.")
            elif choice == "8":
                storage.save(library, data_path)
                print("Saved. Goodbye!")
                break
            else:
                print("Invalid option.")
        except (LibraryError, ValueError) as err:
            print(f"Error: {err}")
