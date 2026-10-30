from catalog.models import (
    Assignment,
    Course,
    Enrollment,
    Lesson,
    Submission,
)
from users.models import User

print("=== SOAL 4b — QUERY DJANGO SHELL ===")

print()
print("--- 4b.1 Semua Course beserta kode dan judulnya ---")
print(f"  (total Course di database: {Course.objects.count()})")
print("  10 baris pertama:")
for c in Course.objects.all().values("code", "title")[:10]:
    print(f"  {c['code']} | {c['title']}")
print("  ... (output dipotong; total 10.022 course termasuk 10.000 dataset performa)")

print()
print("--- 4b.2 Course yang diampu oleh seorang dosen (suprayogi) ---")
dosen = User.objects.get(username="suprayogi")
courses_dosen = Course.objects.filter(lecturer=dosen)
print(f"  (total Course diampu suprayogi: {courses_dosen.count()})")
for c in courses_dosen[:10]:
    print(f"  {c.code} | {c.title}")
print("  ... (10 baris pertama dari 10.002 course)")

print()
print("--- 4b.3 Semua Lesson milik satu Course tertentu (PSS01) ---")
course_pss = Course.objects.get(code="PSS01")
for l in Lesson.objects.filter(course=course_pss).order_by("order"):
    print(f"  {l.order}. {l.title}")

print()
print("--- 4b.4 Jumlah mahasiswa yang terdaftar pada suatu Course ---")
for c in Course.objects.filter(code__in=["PSS01", "BD01"]):
    jumlah = Enrollment.objects.filter(course=c).count()
    print(f"  {c.code} ({c.title}) : {jumlah} mahasiswa")

print()
print("--- 4b.5 Semua Assignment milik suatu Course (PSS01) ---")
for a in Assignment.objects.filter(course=course_pss):
    print(f"  {a.title} | deadline: {a.deadline}")

print()
print("--- 4b.6 Semua Submission milik suatu Assignment (Tugas Django ORM) ---")
assignment = Assignment.objects.get(title="Tugas Django ORM")
for s in Submission.objects.filter(assignment=assignment):
    print(f"  {s.student.username} | nilai: {s.grade} | {s.submitted_at}")
