from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import (
    Assignment,
    Course,
    Enrollment,
    Lesson,
    Submission,
)
from users.models import User


class Command(BaseCommand):
    help = "Membuat sample data idempotent Simple LMS (UTS: dosen, mahasiswa, course, lesson, enrollment, assignment, submission)"

    def handle(self, *args, **options):
        # ==========================================
        # 1. USER (idempotent)
        # ==========================================
        lecturer, _ = User.objects.get_or_create(
            username="suprayogi",
            defaults={
                "email": "suprayogi@udinus.ac.id",
                "role": User.Role.LECTURER,
            },
        )
        if not lecturer.has_usable_password():
            lecturer.set_password("12345")
            lecturer.save(update_fields=["password"])

        student_names = ["faishal", "ardhi", "sahal", "danang", "candra", "rangga"]
        students = []
        for name in student_names:
            student, _ = User.objects.get_or_create(
                username=name,
                defaults={
                    "email": f"{name}@student.udinus.ac.id",
                    "role": User.Role.STUDENT,
                },
            )
            if not student.has_usable_password():
                student.set_password("12345")
                student.save(update_fields=["password"])
            students.append(student)

        # ==========================================
        # 2. COURSE (minimal 2)
        # ==========================================
        course_pss, _ = Course.objects.get_or_create(
            code="PSS01",
            defaults={
                "title": "Pemrograman Sisi Server",
                "description": "Belajar backend development dengan Django.",
                "lecturer": lecturer,
            },
        )
        course_bd, _ = Course.objects.get_or_create(
            code="BD01",
            defaults={
                "title": "Basis Data",
                "description": "Perancangan dan optimasi basis data relasional.",
                "lecturer": lecturer,
            },
        )

        # ==========================================
        # 3. LESSON (minimal 3 pada PSS01)
        # ==========================================
        pss_lessons = [
            "Pengenalan Backend",
            "Pola Arsitektur Backend",
            "Containerisasi dengan Docker",
            "Django Framework & ORM",
            "Database Optimization",
        ]
        for order, title in enumerate(pss_lessons, start=1):
            Lesson.objects.get_or_create(
                course=course_pss,
                order=order,
                defaults={"title": title, "content": f"Materi {title}."},
            )

        bd_lessons = [
            "Perancangan Basis Data",
            "Normalisasi",
            "Index dan Optimasi Query",
        ]
        for order, title in enumerate(bd_lessons, start=1):
            Lesson.objects.get_or_create(
                course=course_bd,
                order=order,
                defaults={"title": title, "content": f"Materi {title}."},
            )

        # ==========================================
        # 4. ENROLLMENT (minimal 2)
        # ==========================================
        enrollments = [
            (students[0], course_pss),  # faishal -> PSS01
            (students[1], course_pss),  # ardhi -> PSS01
            (students[2], course_bd),   # sahal -> BD01
            (students[3], course_bd),   # danang -> BD01
            (students[4], course_pss),  # candra -> PSS01
            (students[5], course_bd),   # rangga -> BD01
        ]
        for student, course in enrollments:
            Enrollment.objects.get_or_create(
                student=student,
                course=course,
            )

        # ==========================================
        # 5. ASSIGNMENT (minimal 1)
        # ==========================================
        assignment_pss, _ = Assignment.objects.get_or_create(
            course=course_pss,
            title="Tugas Django ORM",
            defaults={
                "description": "Implementasikan model dan relationship menggunakan Django ORM.",
                "deadline": timezone.now() + timedelta(days=7),
            },
        )
        assignment_bd, _ = Assignment.objects.get_or_create(
            course=course_bd,
            title="Tugas Perancangan Basis Data",
            defaults={
                "description": "Rancang ERD dan normalisasi sampai 3NF.",
                "deadline": timezone.now() + timedelta(days=10),
            },
        )

        # ==========================================
        # 6. SUBMISSION (minimal 1)
        # ==========================================
        Submission.objects.get_or_create(
            assignment=assignment_pss,
            student=students[0],
            defaults={
                "content": "Saya telah menyelesaikan implementasi Django ORM.",
                "grade": 87.50,
            },
        )
        Submission.objects.get_or_create(
            assignment=assignment_bd,
            student=students[2],
            defaults={
                "content": "ERD dan normalisasi 3NF sudah dikerjakan.",
                "grade": 88.00,
            },
        )

        # ==========================================
        # SELESAI
        # ==========================================
        self.stdout.write(
            self.style.SUCCESS(
                "Sample data berhasil dibuat "
                f"(dosen: {lecturer.username}, "
                f"mahasiswa: {len(students)}, "
                f"course: {Course.objects.count()}, "
                f"lesson: {Lesson.objects.count()}, "
                f"enrollment: {Enrollment.objects.count()}, "
                f"assignment: {Assignment.objects.count()}, "
                f"submission: {Submission.objects.count()})."
            )
        )
