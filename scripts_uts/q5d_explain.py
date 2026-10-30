from catalog.models import Course

print("=== SOAL 5d — QuerySet.explain() ===")

print()
print("--- Query 1: filter by code (unique index) ---")
qs1 = Course.objects.filter(code="PERF05000")
print(qs1.explain())

print()
print("--- Query 2: filter is_active + title (index composite) ---")
qs2 = Course.objects.filter(is_active=True, title="Performance Course 5000")
print(qs2.explain())
