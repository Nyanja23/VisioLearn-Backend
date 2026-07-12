"""Utility functions for VisioLearn backend."""
import random
import string

# Class codes are SPOKEN ALOUD by blind students and captured by speech
# recognition, so the alphabet must be unambiguous by ear:
#   O ↔ 0 ("oh" is heard as zero), I ↔ 1, and near-rhymes that speech
#   engines confuse. Existing codes with these characters remain valid —
#   this only constrains newly generated codes.
_SPEECH_SAFE_CHARS = ''.join(
    c for c in string.ascii_uppercase + string.digits if c not in 'O0I1'
)


def generate_student_code() -> str:
    """
    Generate a unique student code for joining classes.
    Format: SC-XXXX (e.g., SC-9FX2)
    - 'SC' prefix (student code)
    - hyphen
    - 4 random speech-safe alphanumeric characters (uppercase)
    """
    chars = ''.join(random.choices(_SPEECH_SAFE_CHARS, k=4))
    return f"SC-{chars}"


def generate_teacher_code() -> str:
    """
    Generate a unique teacher code for subject teachers to join classes.
    Format: TC-XXXX (e.g., TC-5MK8)
    - 'TC' prefix (teacher code)
    - hyphen
    - 4 random speech-safe alphanumeric characters (uppercase)
    """
    chars = ''.join(random.choices(_SPEECH_SAFE_CHARS, k=4))
    return f"TC-{chars}"

