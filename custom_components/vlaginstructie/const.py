from datetime import date, timedelta

def get_variable_days(year: int):
    """Bereken variabele vlagdagen (Veteranendag en Prinsjesdag)."""
    days = {}

    # Veteranendag: laatste zaterdag in juni
    june = date(year, 6, 30)
    while june.weekday() != 5:  # 5 = zaterdag
        june -= timedelta(days=1)
    days[june.strftime("%d-%m")] = {"name": "Veteranendag", "scope": "alle"}

    # Prinsjesdag: derde dinsdag in september
    sept = date(year, 9, 1)
    tuesday_count = 0
    while True:
        if sept.weekday() == 1:  # 1 = dinsdag
            tuesday_count += 1
            if tuesday_count == 3:
                break
        sept += timedelta(days=1)
    days[sept.strftime("%d-%m")] = {"name": "Prinsjesdag", "scope": "alle"}

    return days
