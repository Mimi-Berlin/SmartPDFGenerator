# -*- coding: utf-8 -*-
"""
report_classifier.py
מטרה: זיהוי סוג דוח נוכחות (Type A או Type B)
"""

def classify_report(text):
    """
    מזהה את סוג הדוח על פי מילות מפתח במבנה
    
    Args:
        text (str): הטקסט שחולץ מה-PDF
        
    Returns:
        str: 'TYPE_A' או 'TYPE_B'
    """
    text_lower = text.lower()
    
    indicators = {
        'type_a': 0,
        'type_b': 0
    }
    
    if 'הפסקה' in text or 'הפסקה' in text_lower:
        indicators['type_b'] += 2
        
    if '100%' in text or '125%' in text or '150%' in text:
        indicators['type_b'] += 3
        
    if 'מקום' in text or 'מקו(' in text:
        indicators['type_b'] += 2
        
    if 'נ.ע.' in text or 'הנשר' in text:
        indicators['type_b'] += 1
    
    if 'מחיר לשעה' in text:
        indicators['type_a'] += 3
        
    if 'סה"כ לתשלום' in text or 'לתשלום' in text:
        indicators['type_a'] += 2
        
    if 'ימי עבודה לחודש' in text or 'יומי עבודה' in text:
        indicators['type_a'] += 2
    
    if indicators['type_b'] > indicators['type_a']:
        return 'TYPE_B'
    else:
        return 'TYPE_A'


def get_report_description(report_type):
    """
    מחזיר תיאור של סוג הדוח
    
    Args:
        report_type (str): 'TYPE_A' או 'TYPE_B'
        
    Returns:
        dict: מידע על הדוח
    """
    if report_type == 'TYPE_A':
        return {
            'type': 'TYPE_A',
            'name': 'דוח נוכחות פשוט',
            'columns': ['תאריך', 'יום', 'כניסה', 'יציאה', 'שעות', 'הערות'],
            'has_overtime': False,
            'has_break': False
        }
    else:
        return {
            'type': 'TYPE_B',
            'name': 'דוח נוכחות מפורט עם שעות נוספות',
            'columns': ['תאריך', 'יום', 'מקום', 'כניסה', 'יציאה', 'הפסקה', 
                       'סה"כ', '100%', '125%', '150%', 'שבת'],
            'has_overtime': True,
            'has_break': True
        }