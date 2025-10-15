# -*- coding: utf-8 -*-
"""
pdf_generator.py
מטרה: יצירת HTML/PDF חדש עם הנתונים המעודכנים
"""

import pandas as pd
import os

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


def generate_html_type_a(df, summary_info):
    """
    מייצר HTML לדוח Type A (פשוט)
    
    Args:
        df (DataFrame): נתוני הדוח
        summary_info (dict): מידע סיכום
        
    Returns:
        str: HTML
    """
    total_hours = df['total'].sum()
    work_days = len(df)
    hourly_rate = summary_info.get('hourly_rate', 32.0)
    total_payment = total_hours * hourly_rate
    
    rows_html = ""
    for idx, row in df.iterrows():
        rows_html += f"""
        <tr>
            <td>{row['date']}</td>
            <td>{row['day']}</td>
            <td>{row['entry']}</td>
            <td>{row['exit']}</td>
            <td>{row['total']:.2f}</td>
            <td></td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: 'Arial', sans-serif;
                direction: rtl;
                text-align: right;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
                border: 2px solid #333;
                padding: 15px;
                background-color: #f5f5f5;
            }}
            .header h2 {{
                margin: 5px 0;
                color: #333;
            }}
            .summary-box {{
                border: 2px solid #333;
                padding: 10px;
                margin-bottom: 20px;
                background-color: #fff;
            }}
            .summary-box table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .summary-box td {{
                padding: 5px;
                border: 1px solid #999;
            }}
            .summary-box .label {{
                background-color: #f0f0f0;
                font-weight: bold;
                width: 40%;
            }}
            table.data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            table.data-table th {{
                background-color: #e0e0e0;
                border: 1px solid #333;
                padding: 8px;
                font-weight: bold;
            }}
            table.data-table td {{
                border: 1px solid #666;
                padding: 8px;
                text-align: center;
            }}
            table.data-table tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>דוח נוכחות חודשי</h2>
        </div>
        
        <div class="summary-box">
            <table>
                <tr>
                    <td class="label">ימי עבודה לחודש:</td>
                    <td>{work_days}</td>
                </tr>
                <tr>
                    <td class="label">סה"כ שעות חודשיות:</td>
                    <td>{total_hours:.2f}</td>
                </tr>
                <tr>
                    <td class="label">מחיר לשעה:</td>
                    <td>₪{hourly_rate:.2f}</td>
                </tr>
                <tr>
                    <td class="label">סה"כ לתשלום:</td>
                    <td>₪{total_payment:.2f}</td>
                </tr>
            </table>
        </div>
        
        <table class="data-table">
            <thead>
                <tr>
                    <th>תאריך</th>
                    <th>יום בשבוע</th>
                    <th>שעת כניסה</th>
                    <th>שעת יציאה</th>
                    <th>סה"כ שעות</th>
                    <th>הערות</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        
        <div class="footer">
            <p>דוח זה נוצר אוטומטית על ידי מערכת ניהול נוכחות</p>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_html_type_b(df, summary_info):
    """
    מייצר HTML לדוח Type B (מפורט עם אחוזים)
    
    Args:
        df (DataFrame): נתוני הדוח
        summary_info (dict): מידע סיכום
        
    Returns:
        str: HTML
    """
    total_days = len(df)
    total_hours = df['total'].sum()
    total_100 = df['regular_100'].sum()
    total_125 = df['overtime_125'].sum()
    total_150 = df['overtime_150'].sum()
    
    rows_html = ""
    for idx, row in df.iterrows():
        row_class = 'sabbath' if row['day'] == 'שבת' else ''
        
        rows_html += f"""
        <tr class="{row_class}">
            <td>{row['date']}</td>
            <td>{row['day']}</td>
            <td>{row.get('location', '')}</td>
            <td>{row['entry']}</td>
            <td>{row['exit']}</td>
            <td>{row['break']}</td>
            <td>{row['total']:.2f}</td>
            <td>{row['regular_100']:.2f}</td>
            <td>{row['overtime_125']:.2f}</td>
            <td>{row['overtime_150']:.2f}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4 landscape;
                margin: 1.5cm;
            }}
            body {{
                font-family: 'Arial', sans-serif;
                direction: rtl;
                text-align: right;
                font-size: 11px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 15px;
                border: 2px solid #000;
                padding: 10px;
                background-color: #e8e8e8;
            }}
            .header h2 {{
                margin: 5px 0;
                color: #000;
            }}
            .header h3 {{
                margin: 3px 0;
                color: #333;
                font-weight: normal;
            }}
            table.data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            table.data-table th {{
                background-color: #d0d0d0;
                border: 1px solid #000;
                padding: 6px;
                font-weight: bold;
                font-size: 10px;
            }}
            table.data-table td {{
                border: 1px solid #666;
                padding: 5px;
                text-align: center;
                font-size: 10px;
            }}
            table.data-table tr.sabbath {{
                background-color: #f0f0f0;
            }}
            table.data-table tr:hover {{
                background-color: #fffacd;
            }}
            .summary-table {{
                margin-top: 15px;
                width: 40%;
                float: left;
                border-collapse: collapse;
            }}
            .summary-table td {{
                border: 1px solid #666;
                padding: 5px;
                font-size: 11px;
            }}
            .summary-table .label {{
                background-color: #e0e0e0;
                font-weight: bold;
                width: 60%;
            }}
            .clearfix {{
                clear: both;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>נ.ע. הנשר בע"מ</h2>
            <h3>דוח נוכחות מפורט עם שעות נוספות</h3>
        </div>
        
        <table class="data-table">
            <thead>
                <tr>
                    <th>תאריך</th>
                    <th>יום</th>
                    <th>מקום ע"נ</th>
                    <th>כניסה</th>
                    <th>יציאה</th>
                    <th>הפסקה</th>
                    <th>סה"כ</th>
                    <th>שעות 100%</th>
                    <th>שעות 125%</th>
                    <th>שעות 150%</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        
        <table class="summary-table">
            <tr>
                <td class="label">ימים:</td>
                <td>{total_days}</td>
            </tr>
            <tr>
                <td class="label">סה"כ שעות:</td>
                <td>{total_hours:.2f}</td>
            </tr>
            <tr>
                <td class="label">שעות 100%:</td>
                <td>{total_100:.2f}</td>
            </tr>
            <tr>
                <td class="label">שעות 125%:</td>
                <td>{total_125:.2f}</td>
            </tr>
            <tr>
                <td class="label">שעות 150%:</td>
                <td>{total_150:.2f}</td>
            </tr>
            <tr>
                <td class="label">בונוס:</td>
                <td>0</td>
            </tr>
            <tr>
                <td class="label">נסיעות:</td>
                <td>0</td>
            </tr>
        </table>
        
        <div class="clearfix"></div>
    </body>
    </html>
    """
    
    return html


def generate_pdf(df, report_type, output_path, summary_info=None):
    """
    מייצר קובץ HTML מהנתונים
    
    Args:
        df (DataFrame): נתוני הדוח
        report_type (str): 'TYPE_A' או 'TYPE_B'
        output_path (str): נתיב לשמירת הקובץ
        summary_info (dict): מידע נוסף לסיכום
        
    Returns:
        bool: האם ההפקה הצליחה
    """
    try:
        if summary_info is None:
            summary_info = {}
        
        if report_type == 'TYPE_A':
            html_content = generate_html_type_a(df, summary_info)
        else:
            html_content = generate_html_type_b(df, summary_info)
        
        if output_path.endswith('.pdf'):
            output_path = output_path.replace('.pdf', '.html')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return True
        
    except Exception as e:
        print(f"שגיאה ביצירת HTML: {e}")
        return False


def generate_simple_pdf(df, report_type, output_path, summary_info=None):
    """
    מייצר PDF פשוט עם טבלה בסיסית
    
    Args:
        df (DataFrame): נתוני הדוח
        report_type (str): 'TYPE_A' או 'TYPE_B'
        output_path (str): נתיב לשמירת ה-PDF
        summary_info (dict): מידע נוסף לסיכום
        
    Returns:
        bool: האם ההפקה הצליחה
    """
    if not FPDF_AVAILABLE:
        return False
    
    try:
        if summary_info is None:
            summary_info = {}
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)
        
        pdf.set_font("Helvetica", 'B', 14)
        if report_type == 'TYPE_A':
            pdf.cell(200, 10, text="Attendance Report - Type A", new_x="LMARGIN", new_y="NEXT", align='C')
        else:
            pdf.cell(200, 10, text="Attendance Report - Type B", new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.ln(5)
        
        if report_type == 'TYPE_A':
            pdf.set_font("Helvetica", size=10)
            total_hours = df['total'].sum()
            work_days = len(df)
            hourly_rate = summary_info.get('hourly_rate', 32.0)
            total_payment = total_hours * hourly_rate
            
            pdf.cell(0, 6, text=f"Work Days: {work_days}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 6, text=f"Total Hours: {total_hours:.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 6, text=f"Hourly Rate: ${hourly_rate:.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 6, text=f"Total Payment: ${total_payment:.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
        
        pdf.set_font("Helvetica", 'B', 9)
        
        if report_type == 'TYPE_A':
            col_widths = [30, 25, 25, 25, 25, 60]
            headers = ['Date', 'Day', 'Entry', 'Exit', 'Hours', 'Notes']
        else:
            col_widths = [25, 20, 20, 20, 20, 20, 20, 20, 20, 20]
            headers = ['Date', 'Day', 'Location', 'Entry', 'Exit', 'Break', 
                      'Total', '100%', '125%', '150%']
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, text=header, border=1, align='C')
        pdf.ln()
        
        pdf.set_font("Helvetica", size=8)
        
        for idx, row in df.iterrows():
            if report_type == 'TYPE_A':
                data = [
                    str(row['date']),
                    "",
                    str(row['entry']),
                    str(row['exit']),
                    f"{row['total']:.2f}",
                    ""
                ]
            else:
                data = [
                    str(row['date']),
                    "",
                    "",
                    str(row['entry']),
                    str(row['exit']),
                    str(row['break']),
                    f"{row['total']:.2f}",
                    f"{row['regular_100']:.2f}",
                    f"{row['overtime_125']:.2f}",
                    f"{row['overtime_150']:.2f}"
                ]
            
            for i, value in enumerate(data):
                pdf.cell(col_widths[i], 7, text=value, border=1, align='C')
            pdf.ln()
        
        if report_type == 'TYPE_B':
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(0, 6, text="Summary:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=9)
            pdf.cell(0, 6, text=f"Total Days: {len(df)}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 6, text=f"Total Hours: {df['total'].sum():.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 6, text=f"100% Hours: {df['regular_100'].sum():.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 6, text=f"125% Hours: {df['overtime_125'].sum():.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 6, text=f"150% Hours: {df['overtime_150'].sum():.2f}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.output(output_path)
        
        return True
        
    except Exception as e:
        print(f"שגיאה ביצירת PDF: {e}")
        return False