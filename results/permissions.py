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
        "خادم",
        "امين اسرة",
        "امين مساعد اسرة",
    ]:
        return user.family_id == family.id

    # خادم / مخدوم
    return False

from results.models import StudentEnrollment


def can_manage_student(user, student):

    print("========== CAN MANAGE STUDENT ==========")
    print("USER:", user.id, user.username)
    print("USER ROLE:", repr(user.role))
    print("STUDENT:", student.id, student.full_name)
    print("STUDENT FAMILY:", student.family_id)

    if user.role == "admin" or user.is_superuser:
        print("ADMIN => TRUE")
        return True

    if user.role == "امين الشمامسة":
        print("AMIN SHAMAMSA => TRUE")
        return True

    if user.role == "امين مرحلة":
        exists = StudentEnrollment.objects.filter(
            student=student,
            family__stage__leaders=user
        ).exists()

        print("AMIN MARHLA =>", exists)

        return exists

    if user.role in [
        "خادم",
        "امين اسرة",
        "امين مساعد اسرة",
    ]:
        exists = StudentEnrollment.objects.filter(
            student=student,
            family=user.family
        ).exists()

        print("FAMILY ROLE =>", exists)

        return exists

    if user.id == student.id:
        print("SELF => TRUE")
        return True

    print("DEFAULT => FALSE")
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