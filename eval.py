import re
from app import answer_question

# (question, [patterns]). A test passes if ANY pattern matches the answer.
# Patterns are case-insensitive regexes. Prefix with "CS:" for case-sensitive.
TESTS = [
    # --- original questions ---
    ("What is the minimum attendance required in each course?", [r"75"]),
    ("Below what attendance percentage is a student not allowed to write the end-semester exam?", [r"65"]),
    ("What is the minimum percentage to pass the end-semester exam in a theory course?", [r"40"]),
    ("What CGPA is needed for First Class with Distinction?", [r"8\.5"]),
    ("How many times can a student withdraw from end-semester exams during the programme?", [r"once", r"one time", r"only one"]),
    ("What is the maximum duration to complete the degree beyond the normal duration?", [r"two", r"\b2\b"]),
    ("What grade is given for marks between 91 and 100?", [r"CS:\bO\b"]),
    ("How many marks is the mid-semester exam for a theory course?", [r"30"]),
    ("What is the capital of France?", [r"couldn.t find"]),          # should be refused

    # --- new questions (answers checked against the regulations PDF) ---
    ("What minimum CGPA is needed to do the final semester project in industry?", [r"7\.5"]),
    ("What minimum attendance is needed to complete an audit course?", [r"65"]),
    ("What is the maximum number of credits a student can earn through online courses?", [r"\bsix\b", r"\b6\b"]),
    ("What is the minimum CGPA required for First Class?", [r"7\.0"]),
    ("What is the minimum CGPA for Second Class?", [r"6\.0"]),
    ("What is the maximum number of students assigned to one faculty mentor?", [r"30"]),
    ("How many working days does the university have in a year?", [r"180"]),
    ("How many hours of training per semester are needed for the Ability Enhancement Activity?", [r"40"]),
    ("Is ragging allowed at the university?", [r"not (at all )?allowed", r"prohibit", r"punitive"]),
    ("What is the hostel fee at SNU Chennai?", [r"couldn.t find"]),  # should be refused
]

def matches(answer, pattern):
    if pattern.startswith("CS:"):
        return re.search(pattern[3:], answer) is not None
    return re.search(pattern, answer, re.I) is not None

correct = 0
for q, patterns in TESTS:
    answer, _ = answer_question(q)
    ok = any(matches(answer, p) for p in patterns)
    correct += ok
    print(("PASS" if ok else "FAIL"), "|", q)
    print("      ->", answer[:110].replace("\n", " "))
print(f"\nScore: {correct}/{len(TESTS)}")