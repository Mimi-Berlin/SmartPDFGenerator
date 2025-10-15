# מערכת עיבוד דוחות נוכחות

מערכת לעיבוד אוטומטי של דוחות נוכחות בפורמט PDF, יצירת וריאציות הגיוניות, והפקת דוחות חדשים.

## תיאור המערכת

המערכת מבצעת את התהליכים הבאים:

1. **חילוץ טקסט מ-PDF סרוק** באמצעות OCR (Tesseract)
2. **זיהוי סוג הדוח** (דוח פשוט או מפורט)
3. **פרסור נתונים** והמרה למבנה מובנה
4. **יצירת וריאציה הגיונית** של זמני עבודה ושעות
5. **הפקת דוחות חדשים** בפורמטים שונים (HTML, Excel, PDF)

## דרישות מקדימות

### תוכנות נדרשות

1. **Python 3.8 ומעלה**
2. **Tesseract OCR** עם תמיכה בעברית
3. **Poppler** להמרת PDF לתמונות

### התקנת Tesseract OCR

#### Windows:

1. הורידו את הקובץ מהכתובת:
   https://github.com/UB-Mannheim/tesseract/wiki
   
2. הורידו: `tesseract-ocr-w64-setup-5.5.0.xxxxx.exe`

3. בזמן ההתקנה:
   - וודאו שמסומן: "Additional language data" -> Hebrew
   - שמרו את נתיב ההתקנה: `C:\Program Files\Tesseract-OCR`

4. הוסיפו את Tesseract ל-PATH:
   - לחצו `Win + R` וכתבו `sysdm.cpl`
   - Advanced -> Environment Variables
   - ערכו את `Path` והוסיפו: `C:\Program Files\Tesseract-OCR`

5. אימות התקנה:
```bash
   tesseract --version
   tesseract --list-langs
```
   וודאו ש-`heb` מופיע ברשימה.

### התקנת Poppler

1. הורידו מ: https://github.com/oschwartz10612/poppler-windows/releases/

2. חלצו את הקבצים לתיקייה: `C:\Program Files\poppler`

3. הוסיפו ל-PATH את התיקייה:
```
   C:\Program Files\poppler\poppler-24.08.0\Library\bin
```

4. אימות:
```bash
   pdftoppm -v
```

## התקנת המערכת

### 1. יצירת סביבת עבודה וירטואלית - ע"מ לשמור על תקינות ההתקנות לפרויקט זה ספציפית.
```bash
cd attendance_report_generator
python -m venv venv
venv\Scripts\activate
```

### 2. התקנת ספריות Python
```bash
pip install pytesseract
pip install Pillow
pip install pdf2image
pip install reportlab
pip install pandas
pip install opencv-python
pip install openpyxl
pip install fpdf2
```

או באמצעות קובץ requirements:
```bash
pip install -r requirements.txt
```

## מבנה הפרויקט
```
attendance_report_generator/
│
├── code/
│   ├── main.py                      # קובץ ראשי להרצה
│   ├── report_classifier.py         # זיהוי סוג דוח
│   ├── report_parser.py             # פרסור נתונים
│   ├── variation_generator.py       # יצירת וריאציות
│   └── pdf_generator.py             # יצירת קבצי פלט
│
├── input_pdfs/                      # תיקיית קלט לדוחות PDF
├── output_pdfs/                     # תיקיית פלט
├── requirements.txt                 # רשימת תלויות
└── README.md                        # מסמך זה
```

## הרצת המערכת

### שימוש בסיסי
```bash
cd code
python main.py
```

המערכת תחפש קבצי PDF בתיקיית `input_pdfs` ותציג רשימה לבחירה.

### הרצה עם נתיב ספציפי
```bash
python main.py path/to/report.pdf
```

### תהליך העיבוד

המערכת תבצע 5 שלבים:

1. **שלב 1: חילוץ טקסט**
   - המרת PDF לתמונה (DPI 300)
   - הרצת OCR עם תמיכה בעברית ואנגלית
   - שמירת הטקסט המלא

2. **שלב 2: זיהוי סוג דוח**
   - TYPE_A: דוח נוכחות פשוט (6 עמודות)
   - TYPE_B: דוח מפורט עם שעות נוספות (11 עמודות)

3. **שלב 3: פרסור נתונים**
   - חילוץ תאריכים, זמנים, שעות
   - המרה למבנה DataFrame

4. **שלב 4: יצירת וריאציה**
   - שינוי זמני כניסה/יציאה בטווח ±20-30 דקות
   - שינוי הפסקות בטווח ±10 דקות
   - חישוב מחדש של סה"כ שעות ואחוזים
   - וולידציה: זמן סיום > זמן התחלה, שעות בטווח סביר

5. **שלב 5: יצירת קבצי פלט**
   - Excel (.xlsx)
   - HTML מעוצב
   - PDF פשוט (אופציונלי) (בגלל שביקשו PDF - אבל לא מצאתי משהו שבאמת יעשה דומה כמו ה-HTML)

### פורמטי פלט

המערכת מייצרת 3 סוגי קבצים:

1. **Excel (.xlsx)**: טבלה מסודרת עם כל הנתונים
2. **HTML (.html)**: דוח מעוצב עם תמיכה בעברית RTL
3. **PDF פשוט** (אם fpdf2 מותקן): דוח בסיסי באנגלית

להמרת HTML ל-PDF מעוצב:
1. פתחו את קובץ ה-HTML בדפדפן
2. לחצו Ctrl+P
3. בחרו "Save as PDF" או "Microsoft Print to PDF"

## דוגמאות שימוש

### עיבוד דוח בודד
```bash
python main.py ../input_pdfs/report_type_a.pdf
```

### עיבוד כל הדוחות בתיקייה
```bash
python main.py
```

והמערכת תציג רשימה לבחירה.

## לוגיקת הוריאציה

המערכת מיישמת כללים דטרמיניסטיים:

### דוח Type A (פשוט):
- זמן כניסה: ±20 דקות
- זמן יציאה: ±20 דקות
- חישוב שעות מחדש

### דוח Type B (מפורט):
- זמן כניסה: ±20 דקות
- זמן יציאה: ±30 דקות
- הפסקה: ±10 דקות (טווח 0-60)
- חלוקה לאחוזים:
  - עד 8 שעות: 100%
  - 8-9 שעות: 100% + 125%
  - מעל 9 שעות: 100% + 125% + 150%

### כללי ולידציה:
- זמן סיום חייב להיות אחרי זמן התחלה
- שעות יומיות: 2-12 שעות
- שעות חודשיות: 60-180 שעות

## מגבלות ידועות

1. **דיוק OCR**: 
   - המערכת תלויה באיכות הסריקה המקורית
   - דוחות עם בעיות איכות עלולים להיתקל בקשיים
   - שיעור הצלחה ממוצע: 75-90%

2. **פורמט PDF**:
   - המערכת מיועדת ל-PDF סרוק
   - PDF דיגיטלי עשוי לדרוש התאמות

3. **תמיכה בשפות**:
   - HTML ו-Excel: תמיכה מלאה בעברית
   - PDF פשוט: אנגלית בלבד

## פתרון בעיות

### שגיאה: "tesseract is not recognized"
```bash
# וודאו שהוספתם ל-PATH ופתחתם Command Prompt חדש
tesseract --version
```

### שגיאה: "Unable to get page count"
```bash
# וודאו שהתקנתם Poppler והוספתם ל-PATH
pdftoppm -v
```

### שגיאה: "No module named 'openpyxl'"
```bash
pip install openpyxl
```

### OCR לא מצליח לקרוא טקסט עברי
```bash
# וודאו שהעברית מותקנת:
tesseract --list-langs
# אם 'heb' לא מופיע, הורידו:
# https://github.com/tesseract-ocr/tessdata/raw/main/heb.traineddata
# והעתיקו ל: C:\Program Files\Tesseract-OCR\tessdata\
```

## שיפורים אפשריים

1. **שדרוג OCR**: שימוש ב-Google Cloud Vision API או AWS Textract
2. **תמיכה בפורמטים נוספים**: Word, CSV
3. **ממשק משתמש גרפי**: GUI עם tkinter או PyQt
4. **בדיקות אוטומטיות**: unittest או pytest
5. **לוגים מפורטים**: logging module
6. **תמיכה במספר שפות**: זיהוי שפה אוטומטי

## רישיון וזכויות יוצרים

פרויקט זה נוצר כחלק ממטלת בית למשרת סטודנט במשרד העבודה.


---

**גרסה**: 1.0
**תאריך עדכון אחרון**: אוקטובר 2025