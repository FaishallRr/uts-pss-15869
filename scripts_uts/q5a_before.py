import time

from django.db import connection
from django.test.utils import CaptureQueriesContext

from catalog.models import Course

print("=== SOAL 5a — Course + Lecturer TANPA select_related() (BEFORE) ===")

start = time.perf_counter()
with CaptureQueriesContext(connection) as ctx:
    result = []
    for course in (
        Course.objects.filter(code__startswith="PERF")
        .order_by("code")[:100]
    ):
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
print("3 query pertama yang tercatat:")
for q in list(ctx.captured_queries)[:3]:
    print(" ", q["sql"][:160])
