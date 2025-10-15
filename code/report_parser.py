# -*- coding: utf-8 -*-
"""
report_parser.py
מטרה: פרסור טקסט מדוח נוכחות למבנה נתונים מסודר
"""

import re
from datetime import datetime
import pandas as pd

def calculate_hours_diff(start_time, end_time):
    """
    מחשב הפרש שעות בין זמנים
    
    Args:
        start_time (str): זמן התחלה
        end_time (str): זמן סיום
        
    Returns:
        float: הפרש בשעות
    """
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        
        if end < start:
            from datetime import timedelta
            end = end.replace(day=start.day + 1)
        
        diff = end - start
        hours = diff.total_seconds() / 3600
        return round(hours, 2)
    except:
        return 0.0

def clean_ocr_text(text):
    """
    מנקה טעויות OCR נפוצות
    
    Args:
        text (str): טקסט גולמי מה-OCR
        
    Returns:
        str: טקסט מנוקה
    """
    # החלפת תווים שגויים נפוצים
    replacements = {
        '|': ' ',
        '‎': '',
        '‏': '',
        'jaa': '',
        'pia': '',
        'ja': '',
        'wow': '',
        'wan': '',
        'nw': '',
        'att': '',
        'mvs': '',
        'ere': '',
        'SR': '',
        'im': '',
        'ce': ''
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # ניקוי רווחים מיותרים - אבל שומר על ירידות שורה
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text

def extract_time(text):
    """
    מחלץ זמן בפורמט HH:MM
    
    Args:
        text (str): טקסט שמכיל זמן
        
    Returns:
        str: זמן או None
    """
    match = re.search(r'\b(\d{1,2}):(\d{2})\b', text)
    if match:
        hour = match.group(1).zfill(2)
        minute = match.group(2)
        return f"{hour}:{minute}"
    return None


def extract_date(text):
    """
    מחלץ תאריך בפורמטים שונים
    
    Args:
        text (str): טקסט שמכיל תאריך
        
    Returns:
        str: תאריך בפורמט DD/MM/YYYY או None
    """
    match = re.search(r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b', text)
    if match:
        day = match.group(1).zfill(2)
        month = match.group(2).zfill(2)
        year = match.group(3)
        
        if len(year) == 2:
            year = f"20{year}"
            
        return f"{day}/{month}/{year}"
    return None


def extract_decimal(text):
    """
    מחלץ מספר עשרוני
    
    Args:
        text (str): טקסט שמכיל מספר
        
    Returns:
        float: מספר או 0.0
    """
    match = re.search(r'\b(\d+\.\d+)\b', text)
    if match:
        return float(match.group(1))
    return 0.0

def identify_day_name(text):
    """
    מזהה שם יום בשבוע
    
    Args:
        text (str): טקסט שמכיל שם יום
        
    Returns:
        str: שם היום או None
    """
    days_full = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
    days_short = {
        'ראש': 'ראשון',
        'שנ': 'שני',
        'שלי': 'שלישי',
        'רבי': 'רביעי',
        'חמי': 'חמישי',
        'שיש': 'שישי',
        'חמיש': 'חמישי',
        'גונן': ''  # טעות OCR נפוצה
    }
    
    # חיפוש שם מלא
    for day in days_full:
        if day in text:
            return day
    
    # חיפוש גרסה קצרה
    for short, full in days_short.items():
        if short in text:
            return full if full else None
    
    return None

def parse_type_b_line(line):
    """
    מפרסר שורה מדוח Type B
    
    Args:
        line (str): שורה מהדוח
        
    Returns:
        dict: נתוני השורה או None
    """
    # חילוץ תאריך
    date = extract_date(line)
    if not date:
        return None
    
    # חילוץ יום בשבוע
    day = identify_day_name(line)
    
    # חילוץ כל הזמנים בשורה
    times = re.findall(r'\b(\d{1,2}:\d{2})\b', line)
    
    # חילוץ כל המספרים העשרוניים
    numbers = re.findall(r'(\d+\.\d+)', line)
    
    # בדיקה - צריך לפחות 2 זמנים ו-4 מספרים
    if len(times) >= 2 and len(numbers) >= 4:
        entry = times[0]
        exit_time = times[1]
        break_time = times[2] if len(times) > 2 else '00:00'
        
        total = float(numbers[0])
        regular_100 = float(numbers[1])
        overtime_125 = float(numbers[2])
        overtime_150 = float(numbers[3])
        
        # חילוץ מיקום
        location = None
        location_pattern = r'(?:ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)\s+([א-ת]+)\s+\d{1,2}:'
        location_match = re.search(location_pattern, line)
        if location_match:
            location = location_match.group(1)
        
        return {
            'date': date,
            'day': day,
            'location': location,
            'entry': entry,
            'exit': exit_time,
            'break': break_time,
            'total': total,
            'regular_100': regular_100,
            'overtime_125': overtime_125,
            'overtime_150': overtime_150
        }
    
    return None

def parse_type_a_line(line):
    """
    מפרסר שורה מדוח Type A - גרסה פשוטה ועמידה
    
    Args:
        line (str): שורה מהדוח
        
    Returns:
        dict: נתוני השורה או None
    """
    # חיפוש תאריך בפורמט D/M/YY או DD/MM/YY
    date_pattern = r'(\d{1,2})/(\d{1,2})/(\d{2})'
    date_match = re.search(date_pattern, line)
    
    if not date_match:
        return None
    
    # בניית תאריך
    day = date_match.group(1).zfill(2)
    month = date_match.group(2).zfill(2)
    year = f"20{date_match.group(3)}"
    date = f"{day}/{month}/{year}"
    
    # חיפוש זמנים - H:MM או HH:MM
    time_pattern = r'(\d{1,2}):(\d{2})'
    times = re.findall(time_pattern, line)
    
    if len(times) < 2:
        return None
    
    entry = f"{times[0][0].zfill(2)}:{times[0][1]}"
    exit_time = f"{times[1][0].zfill(2)}:{times[1][1]}"
    
    # חיפוש שעות (מספר עשרוני)
    hours_pattern = r'(\d+\.\d{2})'
    hours_matches = re.findall(hours_pattern, line)
    
    if hours_matches:
        # קח את המספר האחרון (בדרך כלל זה סה"כ השעות)
        total = float(hours_matches[-1])
    else:
        # אם אין, חשב מהזמנים
        try:
            start_h, start_m = int(times[0][0]), int(times[0][1])
            end_h, end_m = int(times[1][0]), int(times[1][1])
            
            start_total = start_h + start_m / 60
            end_total = end_h + end_m / 60
            
            if end_total < start_total:
                end_total += 24
            
            total = round(end_total - start_total, 2)
        except:
            return None
    
    # ולידציה בסיסית
    if total <= 0 or total > 24:
        return None
    
    # יום בשבוע (אופציונלי)
    day_name = identify_day_name(line)
    
    return {
        'date': date,
        'day': day_name if day_name else '',
        'entry': entry,
        'exit': exit_time,
        'total': total
    }

def parse_report(text, report_type):
    """
    מפרסר את כל הדוח לפי סוגו
    
    Args:
        text (str): הטקסט המלא מה-OCR
        report_type (str): 'TYPE_A' או 'TYPE_B'
        
    Returns:
        pandas.DataFrame: טבלה עם הנתונים
    """
    # ניקוי טקסט
    text = clean_ocr_text(text)
    
    # פיצול לשורות
    lines = text.split('\n')
    
    # רשימה לאחסון השורות המפורסרות
    parsed_data = []
    
    print(f"\n📋 סה\"כ שורות בטקסט: {len(lines)}")
    
    for line in lines:
        # דילוג על שורות ריקות או קצרות מדי
        line = line.strip()
        if len(line) < 15:
            continue
            
        # דילוג על שורות כותרת
        skip_keywords = ['תאריך', 'כניסה', 'יציאה', 'מקום', 'הפסקה', 'DTN', 'בע"מ', 'נ.ע.']
        if any(keyword in line for keyword in skip_keywords):
            continue
        
        # פרסור לפי סוג
        if report_type == 'TYPE_B':
            row_data = parse_type_b_line(line)
        else:
            row_data = parse_type_a_line(line)
        
        if row_data:
            parsed_data.append(row_data)
    
    # המרה ל-DataFrame
    if parsed_data:
        df = pd.DataFrame(parsed_data)
        return df
    else:
        return pd.DataFrame()


def extract_summary_info(text, report_type):
    """
    מחלץ מידע סיכום מהדוח
    
    Args:
        text (str): הטקסט המלא
        report_type (str): סוג הדוח
        
    Returns:
        dict: מידע סיכום
    """
    summary = {}
    
    if report_type == 'TYPE_A':
        days_match = re.search(r'(\d+)\s*ימ', text)
        if days_match:
            summary['work_days'] = int(days_match.group(1))
        
        hours_match = re.search(r'(\d+\.\d+)\s*שעות', text)
        if hours_match:
            summary['monthly_hours'] = float(hours_match.group(1))
        
        price_match = re.search(r'₪?\s*(\d+\.\d+)\s*שעה', text)
        if price_match:
            summary['hourly_rate'] = float(price_match.group(1))
    
    else:
        summary['total_days'] = len(re.findall(r'\d{2}/\d{2}/\d{4}', text))
    
    return summary


# בדיקת המודול
if __name__ == "__main__":
    print("=" * 70)
    print("בדיקת Parser - חילוץ נתונים מטקסט")
    print("=" * 70)
    
    # דוגמה - טקסט Type B
    sample_text = """נ.ע. הנשר DTN ND בע"מ
תאריך מקום כניסה יציאה הפסקה סה"כ 100% 125% 150%
01/02/2023 יום רביעי גונן 08:00 16:00 00:30 7.50 7.50 0.00 0.00 0.00
02/02/2023 יום חמישי גונן 08:00 16:00 00:30 7.50 7.50 0.00 0.00 0.00
05/02/2023 יום ראשון גונן 08:00 16:00 00:30 7.50 7.50 0.00 0.00 0.00"""
    
    print("\n📄 טקסט לדוגמה (Type B):")
    print(sample_text[:200] + "...")
    
    print("\n🔍 מפרסר...")
    df = parse_report(sample_text, 'TYPE_B')
    
    print(f"\n✓ נמצאו {len(df)} שורות נתונים")
    print("\n📊 תצוגה ראשונה של הטבלה:")
    print(df.head())
    
    print("\n" + "=" * 70)
    print("✅ Parser עובד!")
    print("=" * 70)