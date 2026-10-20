"""Core domain classes: Book, Member hierarchy and Loan."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    year: int
    copies: int = 1
    available: Optional[int] = None

    def __post_init__(self) -> None:
        if self.copies < 1:
            raise ValueError("A book must have at least one copy.")
        if self.available is None:
            self.available = self.copies

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        return cls(**data)

    def __str__(self) -> str:
        return (f"{self.title} by {self.author} ({self.year}) "
                f"[ISBN {self.isbn}] - {self.available}/{self.copies} available")


class Member(ABC):
    """Abstract base class for anyone who can borrow books."""

    def __init__(self, member_id: str, name: str, email: str) -> None:
        self.member_id = member_id
        self.name = name
        self.email = email

    @property
    @abstractmethod
    def member_type(self) -> str: ...

    @property
    @abstractmethod
    def max_loans(self) -> int: ...

    @property
    @abstractmethod
    def loan_days(self) -> int: ...

    def to_dict(self) -> dict:
        return {"type": self.member_type, "member_id": self.member_id,
                "name": self.name, "email": self.email}

    @staticmethod
    def from_dict(data: dict) -> "Member":
        kind = data["type"]
        classes = {"student": Student, "teacher": Teacher}
        if kind not in classes:
            raise ValueError(f"Unknown member type: {kind}")
        return classes[kind](data["member_id"], data["name"], data["email"])

    def __str__(self) -> str:
        return f"{self.name} ({self.member_type}, ID {self.member_id})"


class Student(Member):
    member_type = "student"
    max_loans = 3
    loan_days = 14


class Teacher(Member):
    member_type = "teacher"
    max_loans = 5
    loan_days = 30


@dataclass
class Loan:
    isbn: str
    member_id: str
    issue_date: date
    due_date: date
    return_date: Optional[date] = None

    @property
    def is_active(self) -> bool:
        return self.return_date is None

    def days_overdue(self, today: date) -> int:
        end = self.return_date or today
        return max((end - self.due_date).days, 0)

    def to_dict(self) -> dict:
        return {
            "isbn": self.isbn,
            "member_id": self.member_id,
            "issue_date": self.issue_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "return_date": self.return_date.isoformat() if self.return_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Loan":
        return cls(
            data["isbn"], data["member_id"],
            date.fromisoformat(data["issue_date"]),
            date.fromisoformat(data["due_date"]),
            date.fromisoformat(data["return_date"]) if data["return_date"] else None,
        )
