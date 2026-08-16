def can_manage_family(user, family):

    # Admin
    if user.role == "admin" or user.is_superuser:
        return True

    # أمين الشمامسة
    if user.role == "امين الشمامسة":
        return True

    # أمين المرحلة
    if user.role == "امين مرحلة":

        if not family.stage:
            return False

        return family.stage.leaders.filter(
            id=user.id
        ).exists()

    # أمين الأسرة والمساعد
    if user.role in [
        "خادم عادي",
        "امين اسرة",
        "امين مساعد اسرة",
    ]:
        return user.family_id == family.id

    # خادم عادي / مخدوم
    return False

from results.models import StudentEnrollment


def can_manage_student(user, student):

    # Admin
    if user.role == "admin" or user.is_superuser:
        return True

    # أمين الشمامسة
    if user.role == "امين الشمامسة":
        return True

    # أمين المرحلة
    if user.role == "امين مرحلة":
        return StudentEnrollment.objects.filter(
            student=student,
            family__stage__leaders=user
        ).exists()

    # أمين الأسرة والمساعد
    if user.role in [
        "خادم عادي",
        "امين اسرة",
        "امين مساعد اسرة",
    ]:
        return StudentEnrollment.objects.filter(
            student=student,
            family=user.family
        ).exists()

    # المخدوم نفسه
    if user.id == student.id:
        return True

    return False

def can_manage_enrollment(user, enrollment):

    return can_manage_family(
        user,
        enrollment.family
    )


def is_results_admin(user):

    if user.role == "admin" or user.is_superuser:
        return True

    if user.role == "امين الشمامسة":
        return True

    return False