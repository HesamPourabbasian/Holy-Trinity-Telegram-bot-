from persiantools.jdatetime import JalaliDate

def get_today_key():
    today = JalaliDate.today()
    return f"{today.day:02d}-{today.month:02d}"
