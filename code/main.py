# -*- coding: utf-8 -*-
"""
main.py
מטרה: קובץ ראשי שמריץ את כל התהליך מקצה לקצה
"""

import sys
import os
from datetime import datetime

import pytesseract
from pdf2image import convert_from_path
from report_classifier import classify_report, get_report_description
from report_parser import parse_report, extract_summary_info
from variation_generator import generate_variation
from pdf_generator import generate_pdf, generate_simple_pdf, FPDF_AVAILABLE

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_from_pdf(pdf_path):
    """
    חילוץ טקסט מקובץ PDF סרוק
    
    Args:
        pdf_path (str): נתיב לקובץ PDF
        
    Returns:
        str: הטקסט שחולץ
    """
    print("ממיר PDF לתמונה...")
    images = convert_from_path(pdf_path, dpi=300)
    print(f"הומר ל-{len(images)} תמונה/ות")
    
    print("מריץ OCR...")
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(images[0], lang='heb+eng', config=custom_config)
    print(f"חולצו {len(text)} תווים")
    
    return text


def process_attendance_report(input_pdf_path, output_dir="../output_pdfs"):
    """
    מעבד דוח נוכחות מקצה לקצה
    
    Args:
        input_pdf_path (str): נתיב לקובץ PDF המקורי
        output_dir (str): תיקיית פלט
        
    Returns:
        bool: האם העיבוד הצליח
    """
    print("=" * 70)
    print("מתחיל עיבוד דוח נוכחות")
    print("=" * 70)
    
    if not os.path.exists(input_pdf_path):
        print(f"שגיאה: הקובץ לא נמצא: {input_pdf_path}")
        return False
    
    print(f"\nקובץ קלט: {input_pdf_path}")
    
    try:
        print("\n" + "=" * 70)
        print("שלב 1/5: חילוץ טקסט מ-PDF")
        print("=" * 70)
        text = extract_text_from_pdf(input_pdf_path)
        
        text_output = os.path.join(output_dir, "extracted_text.txt")
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"טקסט נשמר ב: {text_output}")
        
        print("\n" + "=" * 70)
        print("שלב 2/5: זיהוי סוג דוח")
        print("=" * 70)
        report_type = classify_report(text)
        report_info = get_report_description(report_type)
        print(f"זוהה כ: {report_info['name']}")
        print(f"סוג: {report_type}")
        print(f"עמודות: {len(report_info['columns'])}")
        
        print("\n" + "=" * 70)
        print("שלב 3/5: פרסור נתונים")
        print("=" * 70)
        df_original = parse_report(text, report_type)
        
        if df_original.empty:
            print("שגיאה: לא נמצאו נתונים בדוח")
            return False
        
        print(f"נמצאו {len(df_original)} שורות נתונים")
        print(f"סה\"כ שעות מקורי: {df_original['total'].sum():.2f}")
        
        summary_info = extract_summary_info(text, report_type)
        
        print("\n" + "=" * 70)
        print("שלב 4/5: יצירת וריאציה")
        print("=" * 70)
        df_variation = generate_variation(df_original, report_type)
        print("וריאציה נוצרה")
        print(f"סה\"כ שעות חדש: {df_variation['total'].sum():.2f}")
        print(f"הפרש: {abs(df_original['total'].sum() - df_variation['total'].sum()):.2f} שעות")
        
        print("\n" + "=" * 70)
        print("שלב 5/5: יצירת קבצי פלט")
        print("=" * 70)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"attendance_report_{report_type.lower()}_{timestamp}"
        
        excel_output = os.path.join(output_dir, f"{base_name}.xlsx")
        df_variation.to_excel(excel_output, index=False, engine='openpyxl')
        print(f"Excel נשמר: {excel_output}")
        
        html_output = os.path.join(output_dir, f"{base_name}.html")
        success_html = generate_pdf(df_variation, report_type, html_output, summary_info)
        if success_html:
            print(f"HTML נוצר: {html_output}")
        
        if FPDF_AVAILABLE:
            pdf_output = os.path.join(output_dir, f"{base_name}_simple.pdf")
            success_pdf = generate_simple_pdf(df_variation, report_type, pdf_output, summary_info)
            if success_pdf:
                print(f"PDF פשוט נוצר: {pdf_output}")
        
        print("\n" + "=" * 70)
        print("העיבוד הושלם בהצלחה")
        print("=" * 70)
        print(f"\nקבצי פלט נוצרו בתיקייה: {output_dir}")
        print(f"Excel: {base_name}.xlsx")
        print(f"HTML: {base_name}.html")
        if FPDF_AVAILABLE:
            print(f"PDF: {base_name}_simple.pdf")
        
        return True
        
    except Exception as e:
        print(f"\nשגיאה בעיבוד: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    נקודת כניסה ראשית לתוכנית
    """
    print("\n" + "=" * 70)
    print("מערכת עיבוד דוחות נוכחות")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]
    else:
        input_dir = "../input_pdfs"
        
        if not os.path.exists(input_dir):
            print(f"\nתיקיית קלט לא נמצאה: {input_dir}")
            print("\nשימוש:")
            print(f"  python main.py <נתיב-לקובץ-PDF>")
            return
        
        pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"\nלא נמצאו קבצי PDF בתיקייה: {input_dir}")
            return
        
        if len(pdf_files) == 1:
            input_pdf = os.path.join(input_dir, pdf_files[0])
            print(f"\nנמצא קובץ: {pdf_files[0]}")
        else:
            print(f"\nנמצאו {len(pdf_files)} קבצי PDF:")
            for i, pdf in enumerate(pdf_files, 1):
                print(f"  {i}. {pdf}")
            
            choice = input("\nבחרי מספר (או Enter לראשון): ").strip()
            
            if choice == "":
                input_pdf = os.path.join(input_dir, pdf_files[0])
            else:
                try:
                    idx = int(choice) - 1
                    input_pdf = os.path.join(input_dir, pdf_files[idx])
                except:
                    print("בחירה לא תקינה")
                    return
    
    success = process_attendance_report(input_pdf)
    
    if success:
        print("\nתהליך הושלם בהצלחה")
    else:
        print("\nתהליך נכשל")
        sys.exit(1)


if __name__ == "__main__":
    main()