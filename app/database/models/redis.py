class OTP():
    key: str
    value: str

    def __init__(self, otp: int, is_profile_id: bool = False, is_mobile_no: bool = False, profile_id: str = "", mobile_no: str = ""):
        if is_profile_id and profile_id:
            self.key = f"otp:profile_id:{profile_id}"
        elif is_mobile_no and mobile_no:
            self.key = f"otp:mobile_no:{mobile_no}"
        else:
            raise Exception(
                "Provide either is_profile_id, profile_id and otp or is_mobile_no, mobile_no and otp")
        self.value = f"{otp}"

    @staticmethod
    def get_key(is_profile_id: bool = False, is_mobile_no: bool = False, profile_id: str = "", mobile_no: str = "") -> str:
        if is_profile_id and profile_id:
            return f"otp:profile_id:{profile_id}"
        elif is_mobile_no and mobile_no:
            return f"otp:mobile_no:{mobile_no}"
        else:
            raise Exception(
                "Provide either is_profile_id, profile_id and otp or is_mobile_no, mobile_no and otp")
