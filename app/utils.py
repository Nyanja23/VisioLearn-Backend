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
