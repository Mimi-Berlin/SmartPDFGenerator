# -*- coding: utf-8 -*-
"""
variation_generator.py
מטרה: יצירת וריאציה הגיונית של נתוני נוכחות
"""

import random
from datetime import datetime, timedelta
import pandas as pd


def parse_time(time_str):
    """
    המרת מחרוזת זמן לאובייקט datetime
    
    Args:
        time_str (str): זמן בפורמט "HH:MM"
        
    Returns:
        datetime: אובייקט זמן
    """
    return datetime.strptime(time_str, "%H:%M")


def format_time(dt):
    """
    המרת datetime למחרוזת זמן
    
    Args:
        dt (datetime): אובייקט זמן
        
    Returns:
        str: זמן בפורמט "HH:MM"
    """
    return dt.strftime("%H:%M")


def add_time_variation(time_str, min_delta=-30, max_delta=30):
    """
    מוסיף וריאציה אקראית לזמן
    
    Args:
        time_str (str): זמן מקורי "HH:MM"
        min_delta (int): שינוי מינימלי בדקות
        max_delta (int): שינוי מקסימלי בדקות
        
    Returns:
        str: זמן חדש "HH:MM"
    """
    time_obj = parse_time(time_str)
    
    # שינוי אקראי בדקות
    delta_minutes = random.randint(min_delta, max_delta)
    new_time = time_obj + timedelta(minutes=delta_minutes)
    
    return format_time(new_time)


def calculate_hours_diff(start_time, end_time, break_minutes=0):
    """
    מחשב הפרש שעות בין שני זמנים
    
    Args:
        start_time (str): זמן התחלה "HH:MM"
        end_time (str): זמן סיום "HH:MM"
        break_minutes (int): דקות הפסקה
        
    Returns:
        float: מספר שעות (עם שתי ספרות אחרי הנקודה)
    """
    start = parse_time(start_time)
    end = parse_time(end_time)
    
    # אם הסיום לפני ההתחלה, כנראה עבר חצות
    if end < start:
        end += timedelta(days=1)
    
    diff = end - start
    total_minutes = diff.total_seconds() / 60
    
    # הפחתת הפסקה
    work_minutes = total_minutes - break_minutes
    
    # המרה לשעות
    hours = work_minutes / 60
    
    return round(hours, 2)


def calculate_overtime_breakdown(total_hours):
    """
    מחלק שעות לפי אחוזים (100%, 125%, 150%)
    
    Args:
        total_hours (float): סה"כ שעות
        
    Returns:
        dict: חלוקה לאחוזים
    """
    regular_100 = 0.0
    overtime_125 = 0.0
    overtime_150 = 0.0
    
    if total_hours <= 8:
        # עד 8 שעות - הכל רגיל
        regular_100 = total_hours
    elif total_hours <= 9:
        # 8-9 שעות: 8 רגיל, השאר 125%
        regular_100 = 8.0
        overtime_125 = total_hours - 8.0
    else:
        # מעל 9: 8 רגיל, 1 ב-125%, השאר 150%
        regular_100 = 8.0
        overtime_125 = 1.0
        overtime_150 = total_hours - 9.0
    
    return {
        'regular_100': round(regular_100, 2),
        'overtime_125': round(overtime_125, 2),
        'overtime_150': round(overtime_150, 2)
    }


def generate_variation_type_a(df_original):
    """
    מייצר וריאציה לדוח Type A
    
    Args:
        df_original (DataFrame): הנתונים המקוריים
        
    Returns:
        DataFrame: נתונים עם וריאציה
    """
    df_new = df_original.copy()
    
    for idx, row in df_new.iterrows():
        # שינוי זמן כניסה (±20 דקות)
        new_entry = add_time_variation(row['entry'], -20, 20)
        
        # שינוי זמן יציאה (±20 דקות)
        new_exit = add_time_variation(row['exit'], -20, 20)
        
        # וידוא שהסיום אחרי ההתחלה
        entry_obj = parse_time(new_entry)
        exit_obj = parse_time(new_exit)
        
        if exit_obj <= entry_obj:
            # אם הסיום לפני או שווה להתחלה, הוסף לפחות שעתיים
            exit_obj = entry_obj + timedelta(hours=2, minutes=random.randint(0, 59))
            new_exit = format_time(exit_obj)
        
        # חישוב שעות חדש
        new_hours = calculate_hours_diff(new_entry, new_exit)
        
        # עדכון הנתונים
        df_new.at[idx, 'entry'] = new_entry
        df_new.at[idx, 'exit'] = new_exit
        df_new.at[idx, 'total'] = new_hours
    
    return df_new


def generate_variation_type_b(df_original):
    """
    מייצר וריאציה לדוח Type B (עם אחוזים)
    
    Args:
        df_original (DataFrame): הנתונים המקוריים
        
    Returns:
        DataFrame: נתונים עם וריאציה
    """
    df_new = df_original.copy()
    
    for idx, row in df_new.iterrows():
        # שינוי זמן כניסה (±20 דקות)
        new_entry = add_time_variation(row['entry'], -20, 20)
        
        # שינוי זמן יציאה (±30 דקות)
        new_exit = add_time_variation(row['exit'], -30, 30)
        
        # שינוי הפסקה (±10 דקות, בטווח 0-60)
        if 'break' in row and row['break']:
            break_time_str = str(row['break'])
            if ':' in break_time_str:
                break_parts = break_time_str.split(':')
                original_break_minutes = int(break_parts[0]) * 60 + int(break_parts[1])
            else:
                original_break_minutes = 30
            
            new_break_minutes = original_break_minutes + random.randint(-10, 10)
            new_break_minutes = max(0, min(60, new_break_minutes))  # בטווח 0-60
            
            new_break = f"{new_break_minutes // 60:02d}:{new_break_minutes % 60:02d}"
        else:
            new_break_minutes = 30
            new_break = "00:30"
        
        # וידוא שהסיום אחרי ההתחלה
        entry_obj = parse_time(new_entry)
        exit_obj = parse_time(new_exit)
        
        if exit_obj <= entry_obj:
            exit_obj = entry_obj + timedelta(hours=3, minutes=random.randint(0, 59))
            new_exit = format_time(exit_obj)
        
        # חישוב סה"כ שעות
        new_total_hours = calculate_hours_diff(new_entry, new_exit, new_break_minutes)
        
        # חלוקה לאחוזים
        overtime = calculate_overtime_breakdown(new_total_hours)
        
        # עדכון הנתונים
        df_new.at[idx, 'entry'] = new_entry
        df_new.at[idx, 'exit'] = new_exit
        df_new.at[idx, 'break'] = new_break
        df_new.at[idx, 'total'] = new_total_hours
        df_new.at[idx, 'regular_100'] = overtime['regular_100']
        df_new.at[idx, 'overtime_125'] = overtime['overtime_125']
        df_new.at[idx, 'overtime_150'] = overtime['overtime_150']
    
    return df_new


def generate_variation(df_original, report_type):
    """
    מייצר וריאציה לפי סוג הדוח
    
    Args:
        df_original (DataFrame): נתונים מקוריים
        report_type (str): 'TYPE_A' או 'TYPE_B'
        
    Returns:
        DataFrame: נתונים עם וריאציה
    """
    if report_type == 'TYPE_A':
        return generate_variation_type_a(df_original)
    else:
        return generate_variation_type_b(df_original)


# בדיקת המודול
if __name__ == "__main__":
    print("=" * 70)
    print("בדיקת Variation Generator - יצירת וריאציה")
    print("=" * 70)
    
    # דוגמה Type B
    sample_data = {
        'date': ['01/02/2023', '02/02/2023', '05/02/2023'],
        'day': ['רביעי', 'חמישי', 'ראשון'],
        'location': ['גונן', 'גונן', 'גונן'],
        'entry': ['08:00', '08:00', '08:00'],
        'exit': ['16:00', '16:00', '16:00'],
        'break': ['00:30', '00:30', '00:30'],
        'total': [7.5, 7.5, 7.5],
        'regular_100': [7.5, 7.5, 7.5],
        'overtime_125': [0.0, 0.0, 0.0],
        'overtime_150': [0.0, 0.0, 0.0]
    }
    
    df_original = pd.DataFrame(sample_data)
    
    print("\n📊 נתונים מקוריים:")
    print(df_original[['date', 'entry', 'exit', 'break', 'total']])
    
    print("\n🎲 מייצר וריאציה...")
    df_variation = generate_variation(df_original, 'TYPE_B')
    
    print("\n✨ נתונים אחרי וריאציה:")
    print(df_variation[['date', 'entry', 'exit', 'break', 'total']])
    
    print("\n📈 השוואת סיכומים:")
    print(f"סה\"כ שעות מקורי: {df_original['total'].sum():.2f}")
    print(f"סה\"כ שעות חדש: {df_variation['total'].sum():.2f}")
    print(f"הפרש: {abs(df_original['total'].sum() - df_variation['total'].sum()):.2f} שעות")
    
    print("\n" + "=" * 70)
    print("✅ Variation Generator עובד!")
    print("=" * 70)