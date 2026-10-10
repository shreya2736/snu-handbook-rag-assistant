from app import answer_question

# (question, keyword that must appear in a correct answer)
TESTS = [
    ("What is the minimum attendance required in each course?", "75"),
    ("Below what attendance percentage is a student not allowed to write the end-semester exam?", "65"),
    ("What is the minimum percentage to pass the end-semester exam in a theory course?", "40"),
    ("What CGPA is needed for First Class with Distinction?", "8.5"),
    ("How many times can a student withdraw from end-semester exams during the programme?", "once"),
    ("What is the maximum duration to complete the degree beyond the normal duration?", "two"),
    ("What grade is given for marks between 91 and 100?", "O"),
    ("How many marks is the mid-semester exam for a theory course?", "30"),
    ("What is the capital of France?", "couldn't find"),   # should be refused
]

correct = 0
for q, kw in TESTS:
    answer, _ = answer_question(q)
    ok = kw.lower() in answer.lower()
    correct += ok
    print(("PASS" if ok else "FAIL"), "|", q, "->", answer[:90].replace("\n", " "))
print(f"\nScore: {correct}/{len(TESTS)}")