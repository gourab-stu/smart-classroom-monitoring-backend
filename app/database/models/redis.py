class OTP:
    key: str
    value: str

    def __init__(self, id: str, otp: int) -> None:
        self.key = f"otp:{id}"
        self.value = f"{otp}"

    @staticmethod
    def get_key(id: str):
        return f"otp:{id}"
