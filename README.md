# Payslip PDF to CSV Converter

A Python tool that extracts data from payslip PDFs and exports the information to a CSV file.

## Features

- Extracts key payslip data: pay date, gross pay, net pay, pension, and worked units/hours
- Calculates UK fiscal year based on pay date
- Renames and organizes processed PDFs by date
- Outputs consolidated data to a sorted CSV file

## Requirements

- Python 3.9+

## Installation

### Using Docker

```bash
docker build -t payslip-parser .
```

### Local Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Place payslip PDF files in the `input/` directory
2. Run the script:

### Local

```bash
python main.py
```

### Docker

```bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output payslip-parser
```

3. Find the results in the `output/` directory:
    - `payslip-log.csv` - consolidated payslip data
    - Renamed PDFs in `YYYY-MM-DD-payslip.pdf` format

## Output CSV Columns

| Column | Description |
|--------|-------------|
| pay_date | Payment date |
| gross_pay | Gross earnings |
| net_pay | Net pay after deductions |
| hours | Calculated hours (units × 8) |
| fiscal_year | UK fiscal year |
| pension | Pension contribution |

## Project Structure

```
text-to-csv/
├── Dockerfile
├── main.py
├── requirements.txt
├── input/          # Place PDFs here
└── output/         # Results saved here
```
