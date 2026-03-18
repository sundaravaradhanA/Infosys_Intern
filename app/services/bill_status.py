from datetime import date

def determine_bill_status(bill):
    today = date.today()
    due_date = bill.due_date.date()

    # ✅ FIX: use status instead
    if bill.status == "Paid":
        return "Paid"
    elif today > due_date:
        return "Overdue"
    else:
        return "Upcoming"