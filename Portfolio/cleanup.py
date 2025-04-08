import csv

input_file = "Portfolio/tabula-icici.csv"      # Your exported CSV from Tabula
output_file = "Portfolio/icici_cleaned.csv" # Output file for Actual import

cleaned_rows = []

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

i = 0
while i < len(lines):
    line = lines[i].strip()
    
    # Check if line starts with a date (simple check for DD-MM-YYYY)
    if len(line) >= 10 and line[2] == '-' and line[5] == '-':
        date = line[:10]
        description = line[11:].strip()
        
        # Grab the second line (details and amount)
        if i + 1 < len(lines):
            second_line = lines[i + 1].strip()
            parts = second_line.rsplit("\t", 1)  # Split on last tab
            if len(parts) == 2:
                more_info, amount = parts
                description += " " + more_info.strip()
                amount = amount.replace(",", "").strip()
                
                # Convert to negative if DR (debit)
                if "DR" in line:
                    amount = "-" + amount

                cleaned_rows.append([date, description, amount])
        i += 2  # Move ahead by two lines
    else:
        i += 1

# Write output
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Date", "Payee", "Amount"])  # Header for Actual
    writer.writerows(cleaned_rows)

print(f"✅ Cleaned {len(cleaned_rows)} transactions into {output_file}")