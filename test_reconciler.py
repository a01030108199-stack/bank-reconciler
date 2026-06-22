import pandas as pd
import os
import sys

# Add directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reconciliation_engine import reconcile_statements, generate_reconciliation_summary, export_reconciliation_excel

def test_matching():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bank_path = os.path.join(current_dir, "bank_statement_sample.xlsx")
    ledger_path = os.path.join(current_dir, "general_ledger_sample.xlsx")
    
    if not os.path.exists(bank_path) or not os.path.exists(ledger_path):
        print("Sample files not found! Please run data_generator.py first.")
        return
        
    print("Loading sample files...")
    df_bank = pd.read_excel(bank_path)
    df_ledger = pd.read_excel(ledger_path)
    
    print(f"Bank records: {len(df_bank)}")
    print(f"Ledger records: {len(df_ledger)}")
    
    print("\nRunning reconciliation engine...")
    df_matched_b, df_unmatched_b, df_matched_l, df_unmatched_l = reconcile_statements(df_bank, df_ledger)
    
    print(f"Matched Bank records: {len(df_matched_b)}")
    print(f"Unmatched Bank records: {len(df_unmatched_b)}")
    print(f"Matched Ledger records: {len(df_matched_l)}")
    print(f"Unmatched Ledger records: {len(df_unmatched_l)}")
    
    summary = generate_reconciliation_summary(df_bank, df_ledger, df_unmatched_b, df_unmatched_l)
    
    print("\n--- RECONCILIATION SUMMARY STATEMENT ---")
    print(f"Bank Ending Balance: {summary['bank_ending_balance']:.2f}")
    print(f"Ledger Ending Balance: {summary['ledger_ending_balance']:.2f}")
    print(f"Deposits in Transit (+): {summary['total_deposits_in_transit']:.2f}")
    print(f"Outstanding Checks (-): {summary['total_outstanding_checks']:.2f}")
    print(f"Adjusted Bank Balance: {summary['adjusted_bank_balance']:.2f}")
    print(f"Direct Bank Credits (+): {summary['total_direct_credits']:.2f}")
    print(f"Bank Charges/Fees (-): {summary['total_bank_charges']:.2f}")
    print(f"Adjusted Ledger Balance: {summary['adjusted_ledger_balance']:.2f}")
    print(f"Difference: {summary['unreconciled_difference']:.2f}")
    
    if abs(summary['unreconciled_difference']) < 0.01:
        print("\nSUCCESS: Balances match exactly! Reconciled difference is 0.00.")
    else:
        print("\nFAILURE: Balances do not match!")
        
    # Test exporting report
    print("\nTesting Excel report export...")
    excel_data = export_reconciliation_excel(summary, df_matched_b, df_unmatched_b, df_matched_l, df_unmatched_l)
    report_path = os.path.join(current_dir, "bank_reconciliation_report_test.xlsx")
    with open(report_path, "wb") as f:
        f.write(excel_data)
    print(f"Report exported successfully: {report_path}")

if __name__ == "__main__":
    test_matching()
