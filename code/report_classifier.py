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
    
    # המרה לאותיות קטנות לחיפוש
    text_lower = text.lower()
    
    # ספירת מאפיינים
    indicators = {
        'type_a': 0,
        'type_b': 0
    }
    
    # מאפיינים של Type B
    if 'הפסקה' in text or 'הפסקה' in text_lower:
        indicators['type_b'] += 2
        
    if '100%' in text or '125%' in text or '150%' in text:
        indicators['type_b'] += 3
        
    if 'מקום' in text or 'מקו(' in text:  # לפעמים OCR טועה
        indicators['type_b'] += 2
        
    if 'נ.ע.' in text or 'הנשר' in text:
        indicators['type_b'] += 1
    
    # מאפיינים של Type A
    if 'מחיר לשעה' in text:
        indicators['type_a'] += 3
        
    if 'סה"כ לתשלום' in text or 'לתשלום' in text:
        indicators['type_a'] += 2
        
    if 'ימי עבודה לחודש' in text or 'יומי עבודה' in text:
        indicators['type_a'] += 2
    
    # החלטה
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
    else:  # TYPE_B
        return {
            'type': 'TYPE_B',
            'name': 'דוח נוכחות מפורט עם שעות נוספות',
            'columns': ['תאריך', 'יום', 'מקום', 'כניסה', 'יציאה', 'הפסקה', 
                       'סה"כ', '100%', '125%', '150%', 'שבת'],
            'has_overtime': True,
            'has_break': True
        }


# פונקציית בדיקה
if __name__ == "__main__":
    # דוגמאות לבדיקה
    
    # דוגמה Type B
    sample_text_b = """
    נ.ע. הנשר DTN ND בע"מ
    תאריך מקום כניסה יציאה הפסקה סה"כ 100% 125% 150%
    יום ראשון 08:00 16:00 00:30 7.50 7.50 0.00 0.00
    """
    
    # דוגמה Type A
    sample_text_a = """
    ימי עבודה לחודש: 21
    סה"כ שעות חודשיות: 63.02
    מחיר לשעה: ₪32.35
    סה"כ לתשלום: ₪2,038.59
    תאריך יום כניסה יציאה שעות
    """
    
    print("=" * 60)
    print("בדיקת זיהוי סוג דוח")
    print("=" * 60)
    
    # בדיקה 1
    type_b = classify_report(sample_text_b)
    info_b = get_report_description(type_b)
    print(f"\nדוגמה 1: {info_b['name']}")
    print(f"זוהה כ: {type_b}")
    print(f"עמודות: {', '.join(info_b['columns'])}")
    
    # בדיקה 2
    type_a = classify_report(sample_text_a)
    info_a = get_report_description(type_a)
    print(f"\nדוגמה 2: {info_a['name']}")
    print(f"זוהה כ: {type_a}")
    print(f"עמודות: {', '.join(info_a['columns'])}")
    
    print("\n" + "=" * 60)