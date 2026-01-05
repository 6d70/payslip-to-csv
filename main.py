import pdfplumber
import pandas as pd
import os
import re
from datetime import datetime

def get_fiscal_year(date_str):
    try:
        clean_date = date_str.replace('-', '/').replace('.', '/')
        dt = datetime.strptime(clean_date, "%d/%m/%Y")

        if dt.month < 4 or (dt.month == 4 and dt.day < 6):
            return str(dt.year)
        else:
            return str(dt.year + 1)
    except:
        return "N/A"

def parse_payslip(pdf_path):
    data = {
        "total_units": 0.0,
        "pay_date": None,
        "gross_pay": "0.00",
        "net_pay": "0.00",
        "pension": "0.00"
    }

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words()
        full_text = page.extract_text() or ""

        units_x0, units_x1 = None, None
        for word in words:
            if "units" in word['text'].lower():
                units_x0 = word['x0'] - 5
                units_x1 = word['x1'] + 5
                break

        if units_x0 is not None:
            for word in words:
                if word['x0'] >= units_x0 and word['x1'] <= units_x1:
                    if re.match(r"^\d+\.\d{2}$", word['text']):
                        data["total_units"] += float(word['text'])

        date_match = re.search(r"(\d{2}[/\-]\d{2}[/\-]\d{4})", full_text)
        data['pay_date'] = date_match.group(1) if date_match else None

        gross_match = re.search(r"Gross\s*(?:Pay|Earnings)?[:\s]*([\d,.]+)", full_text, re.I)
        data['gross_pay'] = gross_match.group(1).replace(',', '') if gross_match else "0.00"

        net_match = re.search(r"Net\s*(?:Pay|Total)?[:\s]*([\d,.]+)", full_text, re.I)
        data['net_pay'] = net_match.group(1).replace(',', '') if net_match else "0.00"

        pension_match = re.search(r"(?:Pension|EE\s*Pens)[:\s]*([\d,.]+)", full_text, re.I)
        data['pension'] = pension_match.group(1).replace(',', '') if pension_match else "0.00"

    data['fiscal_year'] = get_fiscal_year(data['pay_date']) if data['pay_date'] else "N/A"
    data['hours'] = round(data['total_units'] * 8, 2)

    return data

def main():
    input_dir = "input"
    output_dir = "output"
    output_file = os.path.join(output_dir, "payslip-log.csv")

    results = []

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(input_dir, filename)
            try:
                row = parse_payslip(path)
                results.append(row)

                if row["pay_date"]:
                    dt = datetime.strptime(row["pay_date"], "%d/%m/%Y")
                    new_path = os.path.join(output_dir, dt.strftime("%Y-%m-%d") + "-payslip.pdf")

                    with open(path, "rb") as src, open(new_path, "wb") as dst:
                        dst.write(src.read())

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    if results:
        df = pd.DataFrame(results)
        cols = ['pay_date', 'gross_pay', 'net_pay', 'hours', 'fiscal_year', 'pension']
        df = df[cols]
        df['pay_date'] = pd.to_datetime(df['pay_date'], format="%d/%m/%Y", errors='coerce')
        df = df.sort_values(by='pay_date', ascending=True)
        df.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()
