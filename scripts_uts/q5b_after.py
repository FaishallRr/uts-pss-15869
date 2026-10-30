import time

from django.db import connection
from django.test.utils import CaptureQueriesContext

from catalog.models import Course

print("=== SOAL 5b — Course + Lecturer DENGAN select_related('lecturer') (AFTER) ===")

start = time.perf_counter()
with CaptureQueriesContext(connection) as ctx:
    result = []
    courses = (
        Course.objects.filter(code__startswith="PERF")
        .order_by("code")
        .select_related("lecturer")[:100]
    )
    for course in courses:
        result.append((course.code, course.title, course.lecturer.username))
elapsed = time.perf_counter() - start

print("Jumlah Course        :", len(result))
print("Jumlah Query SQL     :", len(ctx.captured_queries))
print("Waktu eksekusi       :", round(elapsed, 4), "detik")
print()
print("Contoh 5 baris hasil:")
for row in result[:5]:
    print(" ", row)
print("  ...")
print()
print("Semua query yang tercatat:")
for q in ctx.captured_queries:
    print(" ", q["sql"][:200])
