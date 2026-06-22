import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sample_data(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    # Base date
    start_date = datetime(2026, 6, 1)
    
    # Generate 40 matching transactions
    matching_data = []
    descriptions = [
        "فاتورة توريد قمح", "سداد دفعة للمورد", "تحصيل من عميل", 
        "فاتورة كهرباء الصومعة", "رواتب الموظفين", "مشتريات قطع غيار",
        "سداد إيجار مخازن", "شراء أدوات مكتبية", "صيانة سيارات النقل"
    ]
    
    current_date = start_date
    for i in range(1, 41):
        current_date += timedelta(days=np.random.randint(0, 2), hours=np.random.randint(1, 12))
        amount = float(np.random.choice([150, 450, 1200, 5000, 12500, 35000, 75000, 120000]))
        is_deposit = np.random.choice([True, False], p=[0.4, 0.6])
        desc = np.random.choice(descriptions)
        ref = f"REF-{1000 + i}"
        doc_num = f"JV-{2000 + i}"
        
        # Bank dates can have a delay of 0-3 days compared to Ledger due to clearing times
        delay = np.random.choice([0, 1, 2, 3], p=[0.6, 0.2, 0.1, 0.1])
        bank_date = current_date + timedelta(days=int(delay))
        
        matching_data.append({
            'ledger_date': current_date.strftime('%Y-%m-%d'),
            'bank_date': bank_date.strftime('%Y-%m-%d'),
            'amount': amount,
            'is_deposit': is_deposit,
            'desc': desc,
            'ref': ref,
            'doc_num': doc_num
        })
        
    # Create Bank Statement records (Deposits = Credit, Withdrawals = Debit in Bank terminology)
    # Deposits / Credit = +
    # Withdrawals / Debit = -
    bank_records = []
    # Create Ledger records (Debit = +, Credit = -)
    ledger_records = []
    
    for item in matching_data:
        # Add to bank
        bank_records.append({
            'التاريخ': item['bank_date'],
            'البيان': f"تسوية {item['desc']}",
            'المرجع': item['ref'],
            'المدين (مسحوبات)': item['amount'] if not item['is_deposit'] else 0.0,
            'الدائن (إيداعات)': item['amount'] if item['is_deposit'] else 0.0,
        })
        
        # Add to ledger
        ledger_records.append({
            'التاريخ': item['ledger_date'],
            'رقم القيد/المستند': item['doc_num'],
            'الشرح': item['desc'],
            'المدين': item['amount'] if item['is_deposit'] else 0.0,
            'الدائن': item['amount'] if not item['is_deposit'] else 0.0,
        })
        
    # --- Add Discrepancies ---
    
    # 1. Outstanding Checks (شيكات صادرة لم تقدم للصرف)
    outstanding_checks = [
        {'التاريخ': '2026-06-28', 'رقم القيد/المستند': 'JV-3001', 'الشرح': 'شيك للمورد - شركة السلام قمح', 'المدين': 0.0, 'الدائن': 45000.0},
        {'التاريخ': '2026-06-29', 'رقم القيد/المستند': 'JV-3002', 'الشرح': 'شيك صيانة مصاعد الصوامع', 'المدين': 0.0, 'الدائن': 8500.0},
    ]
    ledger_records.extend(outstanding_checks)
    
    # 2. Deposits in transit (إيداعات بالطريق)
    deposits_in_transit = [
        {'التاريخ': '2026-06-30', 'رقم القيد/المستند': 'JV-3003', 'الشرح': 'إيداع نقدي حصيلة توريد اليوم', 'المدين': 18000.0, 'الدائن': 0.0}
    ]
    ledger_records.extend(deposits_in_transit)
    
    # 3. Bank Charges / Interest (عمولات بنكية وفوائد)
    bank_only = [
        {'التاريخ': '2026-06-15', 'البيان': 'مصاريف إدارة حساب الربع سنوية', 'المرجع': 'CHG-992', 'المدين (مسحوبات)': 150.0, 'الدائن (إيداعات)': 0.0},
        {'التاريخ': '2026-06-20', 'البيان': 'عمولة تحصيل شيكات مقاصة', 'المرجع': 'CHG-993', 'المدين (مسحوبات)': 75.0, 'الدائن (إيداعات)': 0.0},
        {'التاريخ': '2026-06-30', 'البيان': 'فوائد دائنة مستحقة للحساب', 'المرجع': 'INT-101', 'المدين (مسحوبات)': 0.0, 'الدائن (إيداعات)': 350.0},
    ]
    bank_records.extend(bank_only)
    
    # 4. Direct Transfer from Client (تحويل وارد غير مسجل بالدفاتر)
    bank_only_transfer = [
        {'التاريخ': '2026-06-25', 'البيان': 'تحويل وارد من شركة النيل للمطاحن', 'المرجع': 'TRF-501', 'المدين (مسحوبات)': 0.0, 'الدائن (إيداعات)': 65000.0}
    ]
    bank_records.extend(bank_only_transfer)
    
    # Create DataFrames
    df_bank = pd.DataFrame(bank_records)
    df_ledger = pd.DataFrame(ledger_records)
    
    # Calculate Running Balances
    bank_start = 100000.0
    bank_balances = []
    curr = bank_start
    for _, row in df_bank.iterrows():
        curr = curr - row['المدين (مسحوبات)'] + row['الدائن (إيداعات)']
        bank_balances.append(curr)
    df_bank['الرصيد'] = bank_balances
    
    # General Ledger: Starting Balance = 100,000
    ledger_start = 100000.0
    ledger_balances = []
    curr = ledger_start
    for _, row in df_ledger.iterrows():
        curr = curr + row['المدين'] - row['الدائن']
        ledger_balances.append(curr)
    df_ledger['الرصيد'] = ledger_balances
    
    # Export to Excel files
    bank_path = os.path.join(output_dir, "bank_statement_sample.xlsx")
    ledger_path = os.path.join(output_dir, "general_ledger_sample.xlsx")
    
    df_bank.to_excel(bank_path, index=False)
    df_ledger.to_excel(ledger_path, index=False)
    
    print(f"Generated: {bank_path}")
    print(f"Generated: {ledger_path}")
    return bank_path, ledger_path

if __name__ == "__main__":
    out_dir = r"C:\Users\Akram\.gemini\antigravity\scratch\bank_reconciler"
    generate_sample_data(out_dir)
