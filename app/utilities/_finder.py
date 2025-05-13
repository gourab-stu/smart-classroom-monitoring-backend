from app.database.models import Student, Teacher


async def get_user_by_email(email: str):
    student = await Student.find_one(Student.email == email)
    if student:
        return student
    teacher = await Teacher.find_one(Teacher.email == email)
    return teacher
