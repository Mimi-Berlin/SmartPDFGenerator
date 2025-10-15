# -*- coding: utf-8 -*-
"""
main.py
מטרה: קובץ ראשי שמריץ את כל התהליך מקצה לקצה
"""

import sys
import os
from datetime import datetime

# ייבוא המודולים שלנו
import pytesseract
from pdf2image import convert_from_path
from report_classifier import classify_report, get_report_description
from report_parser import parse_report, extract_summary_info
from variation_generator import generate_variation
from pdf_generator import generate_pdf, generate_simple_pdf, FPDF_AVAILABLE

# הגדרת נתיב Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_from_pdf(pdf_path):
    """
    חילוץ טקסט מקובץ PDF סרוק
    
    Args:
        pdf_path (str): נתיב לקובץ PDF
        
    Returns:
        str: הטקסט שחולץ
    """
    print("⏳ ממיר PDF לתמונה...")
    images = convert_from_path(pdf_path, dpi=300)
    print(f"✓ הומר ל-{len(images)} תמונה/ות")
    
    print("⏳ מריץ OCR (עברית + אנגלית)...")
    # ניסיון עם הגדרות OCR משופרות
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(images[0], lang='heb+eng', config=custom_config)
    print(f"✓ חולצו {len(text)} תווים")
    
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
    print("🚀 מתחיל עיבוד דוח נוכחות")
    print("=" * 70)
    
    # בדיקה שהקובץ קיים
    if not os.path.exists(input_pdf_path):
        print(f"❌ שגיאה: הקובץ לא נמצא: {input_pdf_path}")
        return False
    
    print(f"\n📄 קובץ קלט: {input_pdf_path}")
    
    try:
        # שלב 1: OCR
        print("\n" + "=" * 70)
        print("📥 שלב 1/5: חילוץ טקסט מ-PDF (OCR)")
        print("=" * 70)
        text = extract_text_from_pdf(input_pdf_path)
        
        # שמירת הטקסט המלא
        text_output = os.path.join(output_dir, "extracted_text.txt")
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✓ טקסט נשמר ב: {text_output}")
        
        # שלב 2: זיהוי סוג דוח
        print("\n" + "=" * 70)
        print("🔍 שלב 2/5: זיהוי סוג דוח")
        print("=" * 70)
        report_type = classify_report(text)
        report_info = get_report_description(report_type)
        print(f"✓ זוהה כ: {report_info['name']}")
        print(f"  סוג: {report_type}")
        print(f"  עמודות: {len(report_info['columns'])}")
        
        # שלב 3: פרסור נתונים
        print("\n" + "=" * 70)
        print("📊 שלב 3/5: פרסור נתונים לטבלה")
        print("=" * 70)
        df_original = parse_report(text, report_type)
        
        if df_original.empty:
            print("❌ שגיאה: לא נמצאו נתונים בדוח")
            return False
        
        print(f"✓ נמצאו {len(df_original)} שורות נתונים")
        print(f"  סה\"כ שעות מקורי: {df_original['total'].sum():.2f}")
        
        # חילוץ מידע סיכום
        summary_info = extract_summary_info(text, report_type)
        
        # שלב 4: יצירת וריאציה
        print("\n" + "=" * 70)
        print("🎲 שלב 4/5: יצירת וריאציה הגיונית")
        print("=" * 70)
        df_variation = generate_variation(df_original, report_type)
        print(f"✓ וריאציה נוצרה")
        print(f"  סה\"כ שעות חדש: {df_variation['total'].sum():.2f}")
        print(f"  הפרש: {abs(df_original['total'].sum() - df_variation['total'].sum()):.2f} שעות")
        
        # שלב 5: יצירת קבצי פלט
        print("\n" + "=" * 70)
        print("📄 שלב 5/5: יצירת קבצי פלט")
        print("=" * 70)
        
        # שם בסיס לקבצי פלט
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"attendance_report_{report_type.lower()}_{timestamp}"
        
        # 5.1: שמירת Excel
        excel_output = os.path.join(output_dir, f"{base_name}.xlsx")
        df_variation.to_excel(excel_output, index=False, engine='openpyxl')
        print(f"✓ Excel נשמר: {excel_output}")
        
        # 5.2: יצירת HTML מקצועי
        html_output = os.path.join(output_dir, f"{base_name}.html")
        success_html = generate_pdf(df_variation, report_type, html_output, summary_info)
        if success_html:
            print(f"✓ HTML נוצר: {html_output}")
        
        # 5.3: PDF פשוט (אם fpdf2 מותקן)
        if FPDF_AVAILABLE:
            pdf_output = os.path.join(output_dir, f"{base_name}_simple.pdf")
            success_pdf = generate_simple_pdf(df_variation, report_type, pdf_output, summary_info)
            if success_pdf:
                print(f"✓ PDF פשוט נוצר: {pdf_output}")
        
        # סיכום
        print("\n" + "=" * 70)
        print("✅ העיבוד הושלם בהצלחה!")
        print("=" * 70)
        print(f"\nקבצי פלט נוצרו בתיקייה: {output_dir}")
        print(f"  📊 Excel: {base_name}.xlsx")
        print(f"  🌐 HTML: {base_name}.html")
        if FPDF_AVAILABLE:
            print(f"  📄 PDF: {base_name}_simple.pdf")
        print("\n💡 טיפ: פתחי את קובץ ה-HTML בדפדפן ולחצי Ctrl+P לייצוא ל-PDF מעוצב!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ שגיאה בעיבוד: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    נקודת כניסה ראשית לתוכנית
    """
    print("\n" + "=" * 70)
    print("📋 מערכת עיבוד דוחות נוכחות")
    print("=" * 70)
    
    # בדיקת ארגומנטים
    if len(sys.argv) > 1:
        # הרצה עם נתיב מהשורת פקודה
        input_pdf = sys.argv[1]
    else:
        # ברירת מחדל - בדיקה אם יש קבצים בתיקיית input
        input_dir = "../input_pdfs"
        
        if not os.path.exists(input_dir):
            print(f"\n❌ תיקיית קלט לא נמצאה: {input_dir}")
            print("\nשימוש:")
            print(f"  python main.py <נתיב-לקובץ-PDF>")
            print(f"\nאו:")
            print(f"  העתק קובץ PDF לתיקייה: {input_dir}")
            return
        
        # חיפוש קבצי PDF בתיקייה
        pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"\n❌ לא נמצאו קבצי PDF בתיקייה: {input_dir}")
            print("\nהעתק קובץ PDF לתיקייה זו או ציין נתיב:")
            print(f"  python main.py <נתיב-לקובץ-PDF>")
            return
        
        # אם יש קובץ אחד - השתמש בו
        if len(pdf_files) == 1:
            input_pdf = os.path.join(input_dir, pdf_files[0])
            print(f"\n✓ נמצא קובץ: {pdf_files[0]}")
        else:
            # אם יש יותר מקובץ אחד - הצג רשימה
            print(f"\n📁 נמצאו {len(pdf_files)} קבצי PDF:")
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
                    print("❌ בחירה לא תקינה")
                    return
    
    # עיבוד הדוח
    success = process_attendance_report(input_pdf)
    
    if success:
        print("\n🎉 תהליך הושלם בהצלחה!")
    else:
        print("\n❌ תהליך נכשל")
        sys.exit(1)


if __name__ == "__main__":
    main()