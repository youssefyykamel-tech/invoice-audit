"""
invoice_reader.py - الخطوة 1: قراءة الفاتورة PDF وتحويل البنود لجدول.

طريقة الاستخدام:
1. حط ملف الفاتورة جنب البرنامج ده في نفس المجلد، وسمّيه: invoice.pdf
2. شغّل البرنامج (Ctrl + F5 في VS Code)
3. هيطلعلك ملف جديد اسمه invoice_items.csv تفتحه بالإكسل
"""

import csv
import os
import re

# رقم بالشكل اللي في الفاتورة، زي 14,300.000 أو 5.000
NUM = r"-?[\d,]*\d\.\d{3}"

# سطر البند: ... التاريخ ثم 6 أرقام (الإجمالي، الخصم، مدين/دائن المريض، مدين/دائن التأمين)
LINE_RE = re.compile(
    rf"^(?P<left>.+?)\s+(?P<date>\d{{2}}/\d{{2}}/\d{{4}})"
    rf"\s+(?P<total>{NUM})\s+(?P<discount>{NUM})"
    rf"\s+(?P<pat_debit>{NUM})\s+(?P<pat_credit>{NUM})"
    rf"\s+(?P<ins_debit>{NUM})\s+(?P<ins_credit>{NUM})\s*$"
)

# الجزء الشمال من السطر: الاسم ثم الكمية ثم (اختياري) الوحدة وسعر الوحدة
QTY_RE = re.compile(rf"^(?P<name>.+?)\s+(?P<qty>{NUM})(?:\s+(?P<rest>.*))?$")

DATE_ONLY_RE = re.compile(r"\d{2}/\d{2}/\d{4}")

COLUMNS = [
    "page", "name", "qty", "unit", "unit_price", "date",
    "total", "discount", "pat_debit", "pat_credit", "ins_debit", "ins_credit",
]


def to_number(text):
    """يحوّل '14,300.000' إلى رقم 14300.0"""
    return float(text.replace(",", ""))


def parse_line(line, page_number):
    """يقرا سطر واحد، ويرجّع صف البند، أو None لو السطر مش بند."""
    match = LINE_RE.match(line.strip())
    if not match:
        return None
    left = QTY_RE.match(match.group("left"))
    if not left:
        return None

    unit, unit_price = "", ""
    rest = (left.group("rest") or "").strip()
    price = re.search(NUM + r"$", rest)
    if price:
        unit_price = to_number(price.group(0))
        rest = rest[: price.start()].strip()
    unit = rest

    return {
        "page": page_number,
        "name": left.group("name").strip(),
        "qty": to_number(left.group("qty")),
        "unit": unit,
        "unit_price": unit_price,
        "date": match.group("date"),
        "total": to_number(match.group("total")),
        "discount": to_number(match.group("discount")),
        "pat_debit": to_number(match.group("pat_debit")),
        "pat_credit": to_number(match.group("pat_credit")),
        "ins_debit": to_number(match.group("ins_debit")),
        "ins_credit": to_number(match.group("ins_credit")),
    }


def read_invoice(pdf_path):
    """يقرا كل صفحات الفاتورة ويرجّع (البنود، الأسطر اللي ما اتقرتش)."""
    import pdfplumber  # بنستدعيها هنا عشان الاختبار ما يحتاجهاش

    rows, unread = [], []
    with pdfplumber.open(pdf_path) as pdf:
        for number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            for line in text.splitlines():
                row = parse_line(line, number)
                if row:
                    rows.append(row)
                elif DATE_ONLY_RE.search(line) and "Printed On" not in line:
                    # فيه تاريخ بس السطر ما اتقرأش، يستاهل نراجعه بإيدينا
                    unread.append((number, line.strip()))
    return rows, unread


def save_csv(rows, csv_path):
    # utf-8-sig عشان الإكسل يفتح الملف سليم
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(folder, "invoice.pdf")
    csv_path = os.path.join(folder, "invoice_items.csv")

    if not os.path.exists(pdf_path):
        print("مش لاقي الملف invoice.pdf جنب البرنامج. حطه في نفس المجلد.")
        return

    rows, unread = read_invoice(pdf_path)
    save_csv(rows, csv_path)

    print(f"عدد البنود اللي اتقرأت: {len(rows)}")
    print(f"مجموع عمود الإجمالي: {sum(r['total'] for r in rows):,.3f}")
    print(f"أسطر فيها تاريخ ومش اتقرأت: {len(unread)}")
    for page, line in unread[:10]:
        print(f"  صفحة {page}: {line}")
    print(f"اتحفظ الجدول في: {csv_path}")


if __name__ == "__main__":
    main()
