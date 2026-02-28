from datetime import datetime

def parse_admission_number(admission_no: str):
    """
    Format: 23CAM1001
    23 -> 2023 (joining year)
    CAM -> Course
    1001 -> Roll number
    """
    if len(admission_no) < 7:
        raise ValueError("Invalid Admission Number Format (Example: 23CAM1001)")

    try:
        year_prefix = int(admission_no[:2])
        course = admission_no[2:5].upper()

        joining_year = 2000 + year_prefix
        today = datetime.now()
        year = today.year
        month = today.month

        #Academic year starts in June
        if month < 6:
            current_year = year - joining_year - 1
        else:
            current_year = year - joining_year 

        return {
            "joining_year": joining_year,
            "course": course,
            "current_year": max(current_year, 1)
        }

    except Exception:
        raise ValueError("Invalid Admission Number Format (Use: 23CAM1001)")