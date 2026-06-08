"""Student Grade Calculator

This program manages student records including three test scores and calculates grades.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from statistics import mean
from typing import Dict, List, Optional

DATA_FILE = "student_grades.txt"
FIELDNAMES = ["name", "student_id", "test1", "test2", "test3", "average", "grade"]

GRADE_SCALE = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]


@dataclass
class Student:
    name: str
    student_id: str
    scores: List[float]

    def __post_init__(self) -> None:
        if len(self.scores) != 3:
            raise ValueError("Exactly three test scores are required.")
        for score in self.scores:
            if score < 0 or score > 100:
                raise ValueError("Each score must be between 0 and 100.")

    def average_score(self) -> float:
        return mean(self.scores)

    def letter_grade(self) -> str:
        avg = self.average_score()
        for cutoff, grade in GRADE_SCALE:
            if avg >= cutoff:
                return grade
        return "F"

    def report(self) -> str:
        return (
            f"Student Name: {self.name}\n"
            f"Student ID: {self.student_id}\n"
            f"Test 1: {self.scores[0]:.2f}\n"
            f"Test 2: {self.scores[1]:.2f}\n"
            f"Test 3: {self.scores[2]:.2f}\n"
            f"Average: {self.average_score():.2f}\n"
            f"Letter Grade: {self.letter_grade()}\n"
        )

    def to_record(self) -> str:
        return (
            f"{self.name}|{self.student_id}|{self.scores[0]:.2f}|{self.scores[1]:.2f}|"
            f"{self.scores[2]:.2f}|{self.average_score():.2f}|{self.letter_grade()}"
        )


class StudentGradeCalculator:
    def __init__(self) -> None:
        self.students: Dict[str, Student] = {}
        load_records(self)

    def add_student(self, name: str, student_id: str, scores: List[float]) -> Student:
        key = name.strip().title()
        if not key:
            raise ValueError("Student name cannot be blank.")
        if not student_id.strip():
            raise ValueError("Student ID cannot be blank.")
        if key in self.students:
            raise ValueError(f"Student '{key}' already exists.")
        student = Student(name=key, student_id=student_id.strip(), scores=scores)
        self.students[key] = student
        save_records(self)
        return student

    def get_student(self, name: str) -> Student:
        key = name.strip().title()
        if key not in self.students:
            raise KeyError(f"Student '{key}' not found.")
        return self.students[key]

    def search_students(self, search_term: str) -> List[Student]:
        normalized = search_term.strip().lower()
        return [student for student in self.students.values() if normalized in student.name.lower()]

    def list_students(self) -> List[str]:
        return sorted(self.students.keys())

    def class_average(self) -> Optional[float]:
        all_scores = [score for student in self.students.values() for score in student.scores]
        if not all_scores:
            return None
        return mean(all_scores)

    def class_statistics(self) -> Optional[Dict[str, str]]:
        if not self.students:
            return None
        averages = sorted((student.average_score(), student) for student in self.students.values())
        lowest_avg, lowest_student = averages[0]
        highest_avg, highest_student = averages[-1]
        return {
            "class_average": f"{self.class_average():.2f}",
            "highest": f"{highest_student.name} ({highest_avg:.2f})",
            "lowest": f"{lowest_student.name} ({lowest_avg:.2f})",
        }

    def class_report(self) -> str:
        stats = self.class_statistics()
        if not stats:
            return "No students registered yet."
        return (
            f"Class average: {stats['class_average']}\n"
            f"Highest average: {stats['highest']}\n"
            f"Lowest average: {stats['lowest']}"
        )

    def student_report(self, name: str) -> str:
        return self.get_student(name).report()

    def student_table(self) -> str:
        if not self.students:
            return "No student records found."

        headers = ["Name", "ID", "Test 1", "Test 2", "Test 3", "Average", "Grade"]
        rows = [
            [
                student.name,
                student.student_id,
                f"{student.scores[0]:.2f}",
                f"{student.scores[1]:.2f}",
                f"{student.scores[2]:.2f}",
                f"{student.average_score():.2f}",
                student.letter_grade(),
            ]
            for student in self.students.values()
        ]
        widths = [max(len(str(item)) for item in column) for column in zip(headers, *rows)]
        separator = " | "
        header_row = separator.join(name.ljust(width) for name, width in zip(headers, widths))
        divider = "-+-".join("-" * width for width in widths)
        data_rows = [separator.join(str(item).ljust(width) for item, width in zip(row, widths)) for row in rows]
        return "\n".join([header_row, divider] + data_rows)


def display_message(message: str) -> None:
    print(message)


def read_input(prompt: str) -> str:
    value = input(prompt).strip()
    if value in {"\x1b", "esc", "ESC"}:
        raise KeyboardInterrupt
    return value


def prompt_non_empty(prompt: str) -> str:
    while True:
        value = read_input(prompt)
        if value:
            return value
        display_message("Input cannot be empty. Please try again.")


def prompt_float(prompt: str) -> float:
    while True:
        try:
            value = read_input(prompt)
            number = float(value)
            if number < 0 or number > 100:
                raise ValueError
            return number
        except ValueError:
            display_message("Please enter a valid number between 0 and 100.")


def prompt_three_scores() -> List[float]:
    return [prompt_float(f"Enter score for Test {i + 1}: ") for i in range(3)]


def save_records(calculator: StudentGradeCalculator) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            file.write("|".join(FIELDNAMES) + "\n")
            for student in calculator.students.values():
                file.write(student.to_record() + "\n")
    except OSError as error:
        display_message(f"Error writing to {DATA_FILE}: {error}")


def load_records(calculator: StudentGradeCalculator) -> None:
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                row = line.strip().split("|")
                if line_number == 1 and row == FIELDNAMES:
                    continue
                if len(row) != len(FIELDNAMES):
                    display_message(f"Skipping malformed line {line_number} in {DATA_FILE}.")
                    continue
                try:
                    name, student_id, test1, test2, test3, *_ = row
                    scores = [float(test1), float(test2), float(test3)]
                    student = Student(name=name.strip(), student_id=student_id.strip(), scores=scores)
                    calculator.students[student.name.title()] = student
                except ValueError:
                    display_message(f"Skipping invalid scores on line {line_number}.")
    except OSError as error:
        display_message(f"Error reading {DATA_FILE}: {error}")


def main() -> None:
    calculator = StudentGradeCalculator()
    display_message("Welcome to the Student Grade Calculator.")

    menu = (
        "\nMenu:\n"
        "1 - Add new student record\n"
        "2 - Display all student records\n"
        "3 - Search by student name\n"
        "4 - Show class statistics\n"
        "5 - Quit\n"
        "Type ESC at any prompt to exit.\n"
    )

    try:
        while True:
            display_message(menu)
            choice = read_input("Choose an option (1-5): ")

            if choice == "5":
                display_message("Goodbye.")
                break

            if choice == "1":
                name = prompt_non_empty("Enter student name: ")
                student_id = prompt_non_empty("Enter student ID: ")
                scores = prompt_three_scores()
                try:
                    calculator.add_student(name, student_id, scores)
                    display_message(f"Student '{name.title()}' added successfully.")
                except ValueError as error:
                    display_message(str(error))

            elif choice == "2":
                display_message("\n" + calculator.student_table())

            elif choice == "3":
                search_term = prompt_non_empty("Enter name to search: ")
                matches = calculator.search_students(search_term)
                if not matches:
                    display_message("No matching students found.")
                else:
                    for student in matches:
                        display_message("\n" + student.report())

            elif choice == "4":
                display_message("\n" + calculator.class_report())

            else:
                display_message("Please choose a valid option.")
    except KeyboardInterrupt:
        display_message("\nESC pressed. Exiting program.")


if __name__ == "__main__":
    main()
