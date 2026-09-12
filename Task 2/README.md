# Core Algorithms, OOP Structures & Robust Error Handling

University Registrar data-management engine demonstrating inheritance, encapsulation, polymorphism, custom exceptions, JSON/CSV persistence, and unit testing.

## Run
```bash
python -m venv .venv
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Main classes
- `Person` -> `Student` / `Instructor` inheritance
- Encapsulated validated `email` property
- `display_name()` overridden for polymorphism
- `Course` and `Enrollment` immutable dataclasses
- `Registrar` manages records and enrollments
- `JSONStorage` and `CSVStorage` provide persistence

## Custom errors
`ValidationError`, `DuplicateRecordError`, `RecordNotFoundError`, `EnrollmentError`, and `StorageError`.

The test suite covers successful operations, invalid input, duplicate records, enrollment errors, JSON/CSV round trips, and malformed JSON.
