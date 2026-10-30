# UTS Pemrograman Sisi Server — Simple LMS

Midterm exam (UTS) submission for **Pemrograman Sisi Server (PSS)**.

A simple Learning Management System (LMS) backend built with **Django + PostgreSQL**,
fully containerized with **Docker Compose**.

| | |
|---|---|
| **Name** | Faishal Rasyid Rusianto |
| **NIM** | A11.2024.15869 |
| **Class** | A11.4703 |
| **Lecturer** | Suprayogi, M.Kom. |
| **Report** | [Laporan_UTS_PSS_Faishal_15869.pdf](Laporan_UTS_PSS_Faishal_15869.pdf) |

## Project History

This repository grew through the semester:

1. **Week 4 — Django ORM & Models**  
   Custom `User` model with roles, plus `Course`, `Lesson`, `Enrollment`,
   `Assignment`, `Submission`. Seed command, admin registration, unit tests.
2. **Week 5 — Database & Performance Optimization**  
   N+1 query problem, `select_related`, `prefetch_related`, `QuerySet.explain()`,
   and index optimization on 10,000+ courses.
3. **UTS — Exam Evidence**  
   Real Docker/ORM/optimization experiment outputs, architecture diagram,
   terminal screenshots, and the full report PDF.

## Features

- Custom user model with role (ADMIN / LECTURER / STUDENT)
- Course catalog with lecturer (ForeignKey), lessons, enrollments
- Assignments and student submissions with grades
- Idempotent seed command (`seed_demo`)
- Performance dataset generators (10,000 courses)
- Query optimization scripts with captured evidence (`scripts_uts/`)
- Unit tests (3 tests, all passing)

## Requirements

- Windows + VS Code (or any OS with Docker)
- Docker Desktop — Python, Django, and PostgreSQL run inside containers,
  no need to install them on the host

## How to Run (Reproduce)

```powershell
# 1. clone
git clone https://github.com/FaishallRr/uts-pss-15869.git
cd uts-pss-15869

# 2. environment file
copy .env.example .env

# 3. build and start both containers (app + db)
docker compose build
docker compose up -d
docker compose ps          # both "app" and "db" should be Up

# 4. create database tables
docker compose exec app python manage.py migrate

# 5. seed sample data (safe to run twice)
docker compose exec app python manage.py seed_demo

# 6. run tests
docker compose exec app python manage.py test catalog

# 7. open the app
# http://localhost:8000/admin/  (username: admin)
```

All Django commands run inside the `app` container:

```powershell
docker compose exec app python manage.py ...
```

## Environment Variables

`.env` (not committed, see `.env.example`):

```
DB_NAME=lms_db
DB_USER=lms_user
DB_PASSWORD=lms_password
```

`config/settings.py` reads these from the environment (`HOST=db`, `PORT=5432`).

## Project Structure

```
uts-pss-15869/
├── manage.py
├── config/                          # settings, urls, wsgi/asgi
├── users/                           # custom User (ADMIN/LECTURER/STUDENT) + admin
├── catalog/                         # Course, Lesson, Enrollment, Assignment, Submission
│   └── management/commands/
│       ├── seed_demo.py             # UTS seed data (idempotent)
│       ├── generate_performance_data.py
│       └── generate_relationship_data.py
├── scripts_uts/                     # UTS experiment scripts
│   ├── q4a_check_data.py            # verify seed data
│   ├── q4b_queries.py               # 6 ORM queries (Soal 4b)
│   ├── q5a_before.py                # N+1 without select_related
│   ├── q5b_after.py                 # 1 query with select_related
│   ├── q5c_prefetch.py              # prefetch_related comparison
│   ├── q5d_explain.py               # QuerySet.explain()
│   ├── generate_images.py           # architecture diagram + screenshots
│   ├── generate_report.py           # builds the report PDF
│   └── out/                         # captured real outputs (.txt)
├── docs/images/                     # arsitektur.png + terminal screenshots
├── Laporan_UTS_PSS_Faishal_15869.pdf
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .env.example
└── README.md
```

## ORM Experiments (Soal 4 & 5)

Run these inside Django shell or as scripts:

```powershell
docker compose exec app python manage.py shell
```

```python
# Soal 4b — sample queries
from catalog.models import Course, Lesson, Assignment, Submission, Enrollment
from users.models import User

Course.objects.all().values("code", "title")            # all courses
dosen = User.objects.get(username="suprayogi")
Course.objects.filter(lecturer=dosen)                   # courses by lecturer
course = Course.objects.get(code="PSS01")
Lesson.objects.filter(course=course).order_by("order")  # lessons of a course
Enrollment.objects.filter(course=course).count()        # students enrolled
Assignment.objects.filter(course=course)                # assignments
assignment = Assignment.objects.get(title="Tugas Django ORM")
Submission.objects.filter(assignment=assignment)        # submissions
```

```powershell
# Soal 5 — optimization experiments (real captured outputs in scripts_uts/out/)
docker compose exec app python manage.py shell -c "exec(open('/app/scripts_uts/q5a_before.py').read())"
```

Or run each script file from `scripts_uts/`. Real outputs:

| Script | Result |
|---|---|
| `q5a_before.py` | 100 courses, **101 queries**, 0.0881s (N+1 problem) |
| `q5b_after.py` | 100 courses, **1 query**, 0.0222s (`select_related`) |
| `q5c_prefetch.py` | **2 queries** with prefetch vs **51 queries** without |
| `q5d_explain.py` | both queries use **Index Scan** (not Seq Scan) |

## Regenerate Images & Report (host machine)

```powershell
pip install pillow fpdf2 pymupdf
python scripts_uts/generate_images.py      # docs/images/*.png
python scripts_uts/generate_report.py      # Laporan_UTS_PSS_Faishal_15869.pdf
```

## Seed Data

| Username | Role | Password | Notes |
|---|---|---|---|
| `admin` | ADMIN | set during createsuperuser | Django admin |
| `suprayogi` | LECTURER | `12345` | teaches PSS01, BD01 |
| `faishal` | STUDENT | `12345` | enrolled in PSS01 |
| `ardhi`, `sahal`, `danang`, `candra`, `rangga` | STUDENT | `12345` | enrolled in PSS01 / BD01 |

Courses: `PSS01` (Pemrograman Sisi Server, 5 lessons), `BD01` (Basis Data, 3 lessons),
plus 10,000 `PERF*` courses for performance experiments.

> Local development credentials only. Never commit real secrets
> (`.env` is in `.gitignore`).

## License

For educational purposes (UTS submission).
