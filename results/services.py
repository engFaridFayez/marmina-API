from collections import defaultdict

from results.models import StudentEnrollment


def calculate_annual_status(enrollment):

    results = enrollment.results.select_related(
        "subject_exam__subject",
        "subject_exam__exam",
    )

    # ==========================================
    # إجمالي درجات كل مادة خلال السنة
    # ==========================================

    subject_points = defaultdict(float)

    # ==========================================
    # المواد الموجودة في النتائج
    # ==========================================

    subjects = {}

    for result in results:

        # ======================================
        # كل النتائج أصبحت SubjectExam
        # ======================================

        if not result.subject_exam:
            continue

        subject = result.subject_exam.subject

        subject_points[subject.id] += result.points
        subjects[subject.id] = subject

    # ==========================================
    # حساب المواد الراسبة
    # ==========================================

    failed_subjects = 0
    music_failed = False

    for subject_id, subject in subjects.items():

        total_points = subject_points[subject_id]

        # ======================================
        # الألحان
        # ======================================

        if subject.name == "الالحان":

            if total_points < subject.success_grade:
                music_failed = True

        # ======================================
        # الحضور والغياب
        # ======================================

        elif subject.name == "الحضور والغياب":

            # الحضور والغياب لا يؤثر على الترقية
            continue

        # ======================================
        # باقي المواد
        # ======================================

        else:

            if total_points < subject.success_grade:
                failed_subjects += 1

    # ==========================================
    # قرار السنة
    # ==========================================

    # راسب في الألحان
    if music_failed:
        return "راسب"

    # راسب في مادتين أو أكثر
    if failed_subjects >= 2:
        return "راسب"

    # صفر أو مادة واحدة راسبة
    return "ناجح"


def update_annual_status(enrollment):

    status = calculate_annual_status(enrollment)

    enrollment.status = status

    enrollment.save(
        update_fields=["status"]
    )

    return status