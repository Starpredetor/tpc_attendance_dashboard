import csv


file = "student.csv"

with open(file, "r") as f:
    reader = csv.reader(f)
    student_object = {}
    for row in reader:
        student_object[row[0]] = {
            "name": row[0],
            "roll_number": row[1],
            "branch": row[2],
            "batch": row[3],
            "email_id": row[4],
            "contact_number": row[5],
            "parent_email": row[6],
            "parent_contact": row[7],
            "parent_alternate_email": row[8],
            "parent_alternate_contact": row[9],
        }
with open("student_data.json", "w") as f:
    import json

    json.dump(student_object, f, indent=4)