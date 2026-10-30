from catalog.models import (
    Assignment,
    Course,
    Enrollment,
    Lesson,
    Submission,
)
from users.models import User

print("=== CEK DATA UTS SOAL 4a ===")
print("Dosen (role LECTURER) :", User.objects.filter(role="LECTURER").count())
print("Mahasiswa (STUDENT)   :", User.objects.filter(role="STUDENT").count())
print("Course                :", Course.objects.count())
print("  - PSS01 lessons     :", Lesson.objects.filter(course__code="PSS01").count())
print("  - BD01 lessons      :", Lesson.objects.filter(course__code="BD01").count())
print("Enrollment            :", Enrollment.objects.count())
print("Assignment            :", Assignment.objects.count())
print("Submission            :", Submission.objects.count())
print()
print("Daftar Course (kode, judul, dosen):")
for c in Course.objects.filter(code__in=["PSS01", "BD01"]).select_related("lecturer"):
    print(f"  {c.code} | {c.title} | dosen: {c.lecturer.username}")
print()
print("Daftar Mahasiswa terdaftar (PSS01 & BD01):")
for e in Enrollment.objects.filter(
    course__code__in=["PSS01", "BD01"]
).select_related("student", "course"):
    print(f"  {e.student.username} -> {e.course.code}")
