"""Utility functions for VisioLearn backend."""
import random
import string


def generate_class_code() -> str:
    """
    Generate a unique class code for teachers.
    Format: XX-XXXX (e.g., AB-1234)
    - 2 uppercase letters
    - hyphen
    - 4 digits
    Total possibilities: 26*26*10*10*10*10 = ~6.76 million unique codes
    """
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"{letters}-{numbers}"


def generate_student_code() -> str:
    """
    Generate a unique student code for joining classes.
    Format: SC-XXXX (e.g., SC-9FX2)
    - 'SC' prefix (student code)
    - hyphen
    - 4 random alphanumeric characters (case insensitive, uppercase)
    """
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"SC-{chars}"


def generate_teacher_code() -> str:
    """
    Generate a unique teacher code for subject teachers to join classes.
    Format: TC-XXXX (e.g., TC-5MK8)
    - 'TC' prefix (teacher code)
    - hyphen
    - 4 random alphanumeric characters (case insensitive, uppercase)
    """
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"TC-{chars}"

