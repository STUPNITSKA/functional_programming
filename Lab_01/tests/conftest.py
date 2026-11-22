import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import Registration


@pytest.fixture
def sample_registrations() -> list[Registration]:
    return [
        {
            "id": 1,
            "course": "Python",
            "price": 1000.0,
            "student_status": "student",
            "courses_count": 3,
        },
        {
            "id": 2,
            "course": "SQL",
            "price": 800.0,
            "student_status": "regular",
            "courses_count": 1,
        },
        {
            "id": 3,
            "course": "Haskell",
            "price": 1200.0,
            "student_status": "regular",
            "courses_count": 4,
        },
    ]
