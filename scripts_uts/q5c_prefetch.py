import time

from django.db import connection
from django.test.utils import CaptureQueriesContext

from catalog.models import Course

print("=== SOAL 5c — Course + Lesson DENGAN prefetch_related('lessons') ===")

start = time.perf_counter()
with CaptureQueriesContext(connection) as ctx:
    courses = (
        Course.objects.filter(code__startswith="PERF")
        .order_by("code")
        .prefetch_related("lessons")[:50]
    )
    result = []
    for course in courses:
        titles = [lesson.title for lesson in course.lessons.all()]
        result.append((course.code, len(titles), titles[:3]))
elapsed = time.perf_counter() - start

print("Jumlah Course        :", len(result))
print("Jumlah Query SQL     :", len(ctx.captured_queries), "(1 query Course + 1 query Lesson = 2)")
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

print()
print("=== PERBANDINGAN: TANPA prefetch (BEFORE) ===")
start = time.perf_counter()
with CaptureQueriesContext(connection) as ctx:
    courses = (
        Course.objects.filter(code__startswith="PERF")
        .order_by("code")[:50]
    )
    for course in courses:
        titles = [lesson.title for lesson in course.lessons.all()]
elapsed = time.perf_counter() - start
print("Jumlah Course        : 50")
print("Jumlah Query SQL     :", len(ctx.captured_queries), "(1 + 50 = 51, N+1)")
print("Waktu eksekusi       :", round(elapsed, 4), "detik")
