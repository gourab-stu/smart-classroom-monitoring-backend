import random
import string


def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(population=string.ascii_uppercase + string.digits, k=length))
