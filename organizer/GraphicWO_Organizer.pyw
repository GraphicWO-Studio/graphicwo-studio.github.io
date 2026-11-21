# -*- coding: utf-8 -*-
"""
منظّم الملفات - GraphicWO File Organizer
تطوير: GraphicWO  —  kick.com/graphicwo
يفحص مجلداً ويعرض الملفات مقسومة حسب النوع واللاحقة والحجم،
ويسمح بنقلها وتنظيمها تلقائياً مع إمكانية التراجع، وكل شي قابل للتحكم من الإعدادات.
يعمل على Windows / macOS / Linux - يحتاج Python 3.8+ فقط.
"""
import os
import sys
import json
import shutil
import threading
import subprocess
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ------------------------------------------------------------------ اللغات (عربي / English / Français)

def _detect_lang():
    path = os.path.join(os.path.expanduser("~"), ".graphicwo_organizer_settings.json")
    try:
        with open(path, encoding="utf-8") as fh:
            saved = json.load(fh)
        if saved.get("lang") in ("ar", "en", "fr"):
            return saved["lang"]
        return "ar"  # مستخدم قديم قبل إضافة اللغات
    except (OSError, ValueError):
        pass
    code = ""
    try:
        import locale
        if sys.platform.startswith("win"):
            import ctypes
            code = locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(), "")
        else:
            code = locale.getlocale()[0] or os.environ.get("LANG", "")
    except Exception:  # noqa
        pass
    code = (code or "").lower()[:2]
    return code if code in ("ar", "fr") else "en"


LANG = _detect_lang()
RTL = LANG == "ar"
SR, SL = ("right", "left") if RTL else ("left", "right")   # جهة البداية / النهاية
AE = "e" if RTL else "w"
JR = "right" if RTL else "left"
TR = {
"en": {
"\n\nفشل نقل {0} ملف:\n": "\n\nFailed to move {0} file(s):\n",
"\n\nما انحذفوا ({0}):\n": "\n\nNot deleted ({0}):\n",
"   |   المحدد: {0} ملف ({1})": "   |   Selected: {0} file(s) ({1})",
"   الرقم يبدأ من:": "   Start number:",
"  —  الجدول يعرض أول {0} فقط، لكن «نقل كل المعروض» يشمل الكل": "  —  the table shows the first {0} only, but “Move all shown” includes everything",
"1 – 10 ميغا": "1 – 10 MB",
"10 – 100 ميغا": "10 – 100 MB",
"100 ميغا – 1 غيغا": "100 MB – 1 GB",
"{0}   ←   {1} ملف": "{0}   ←   {1} file(s)",
"{0}  ({1:,} بايت)": "{0}  ({1:,} bytes)",
"{0}  •  الإصدار {1}": "{0}  •  version {1}",
"{0} بايت": "{0} B",
"{0} مجموعة  •  {1} صورة متشابهة  •  المحدد: {2} ({3})": "{0} group(s)  •  {1} similar images  •  selected: {2} ({3})",
"{0} مجموعة  •  {1} نسخة زايدة  •  بتوفّر {2}": "{0} group(s)  •  {1} extra copies  •  saves {2}",
"{date} بياخد تاريخ التصوير من الكاميرا للصور، وإلا تاريخ التعديل": "{date} uses the camera's capture date for photos, otherwise the modified date",
"آخر 30 يوم": "Last 30 days",
"آخر 7 أيام": "Last 7 days",
"آخر تعديل": "Modified",
"آخر سنة": "Last year",
"أخرى": "Other",
"أصغر من 1 ميغا": "Under 1 MB",
"أقدم من سنة": "Older than a year",
"أقصى عدد ملفات يُعرض بالجدول:": "Max files shown in the table:",
"أكبر من 1 غيغا": "Over 1 GB",
"أول حرف كبير": "Title Case",
"إرجاع الأنواع للوضع الافتراضي؟": "Restore default types?",
"إظهار لوحة المعاينة": "Show preview panel",
"إعادة تسمية": "Rename",
"إعادة تسمية {0} ملف ({1})": "Rename {0} file(s) ({1})",
"إعادة تسمية {0} ملف؟\n(بتقدر تتراجع بعدين)": "Rename {0} file(s)?\n(You can undo later)",
"إعادة تسمية جماعية": "Batch rename",
"إعادة تسمية...": "Rename...",
"إغلاق": "Close",
"إلغاء": "Cancel",
"اختار درجة التشابه واكبس «ابحث».": "Choose a similarity level and press “Search”.",
"اختار ملف لتشوف معاينته": "Select a file to preview it",
"اختار نوع من القائمة وعدّل لواحقه (افصل بينها بمسافة). الملفات اللي لاحقتها مو موجودة بتروح لـ «أخرى».": "Pick a type and edit its extensions (separated by spaces). Files with unlisted extensions go to “Other”.",
"اختر المجلد": "Choose folder",
"اختر المجلد الذي سيتم النقل إليه": "Choose the destination folder",
"اختر مجلداً ثم اضغط «فحص».": "Choose a folder, then press “Scan”.",
"اختر مجلداً صحيحاً أولاً.": "Choose a valid folder first.",
"اسألني للتأكيد قبل النقل": "Ask for confirmation before moving",
"استبدال:": "Replace:",
"اسم الملف": "File name",
"اسم النوع (هو اسم المجلد وقت التنظيم):": "Type name (used as folder name when organizing):",
"اسم مجلد الملفات غير المصنفة:": "Folder name for unclassified files:",
"افحص مجلداً أولاً.": "Scan a folder first.",
"الأبعاد": "Dimensions",
"الأحرف:": "Case:",
"الألوان:": "Colors:",
"الأنواع واللواحق": "Types & extensions",
"الإعدادات": "Settings",
"الاسم": "Name",
"الاسم الجديد": "New name",
"الاسم الحالي": "Current name",
"الاسم_001": "name_001",
"التاريخ": "Date",
"التاريخ (الأقدم أولاً)": "Date (oldest first)",
"التاريخ:": "Date:",
"التراجع عن آخر عملية «{0}»؟\n{1} ملف بيرجعوا متل ما كانوا.\n(العملية من: {2})": "Undo the last “{0}”?\n{1} file(s) will be restored.\n(from: {2})",
"الترتيب الحالي": "Current order",
"الترقيم حسب:": "Number by:",
"التصنيف": "Category",
"الحجم": "Size",
"الحجم الكلي": "Total size",
"الحجم:": "Size:",
"الخط «{0}» مو منزّل على الجهاز — رح يستخدم {1} لحد ما تنزّله أو تحطّه بمجلد fonts": "Font “{0}” isn't installed — using {1} until you install it or put it in the fonts folder",
"الخط:": "Font:",
"الصور المتشابهة": "Similar images",
"العدد": "Count",
"الكل": "All",
"اللاحقة": "Extension",
"اللواحق:": "Extensions:",
"المجلد:": "Folder:",
"المجلدات الجديدة تنعمل داخل:": "New folders are created in:",
"المحددة": "selected",
"المظهر والخط": "Appearance & font",
"المعاينة": "Preview",
"المعروض: {0}": "Showing: {0}",
"المعروض: {0} ملف ({1})": "Showing: {0} file(s) ({1})",
"المعروضة": "shown",
"المعروضة بس": "Shown only",
"المكان": "Location",
"الملف": "File",
"الملفات المعروضة حالياً فقط ({0})": "Only files currently shown ({0})",
"الملفات المكررة": "Duplicate files",
"الملفات:": "Files:",
"النسبة": "Share",
"النوع": "Type",
"النوع / اللاحقة": "Type / extension",
"الوقت": "Time",
"اليوم": "Today",
"انحذف {0} ملف لسلة المحذوفات 🗑": "{0} file(s) moved to the Recycle Bin 🗑",
"بحث:": "Search:",
"بدون لاحقة": "No extension",
"بـ": "with",
"تاريخ الإنشاء": "Created",
"تاريخ التصوير/التعديل": "Photo/modified date",
"تجاهل الملفات والمجلدات المخفية": "Ignore hidden files and folders",
"تسمية": "Rename",
"تطوير وتصميم: {0}": "Developed & designed by {0}",
"تطوير: {0}": "by {0}",
"تغيير": "Change",
"تم إرجاع {0} ملف ✅": "{0} file(s) restored ✅",
"تم تحديد {0} ملف": "{0} files selected",
"تم نسخ مسار {0} ملف 📋": "Copied the path of {0} file(s) 📋",
"تم نقل {0} ملف ✅": "{0} file(s) moved ✅",
"تمت إعادة تسمية {0} ملف ✅": "{0} file(s) renamed ✅",
"تنظيم تلقائي": "Auto organize",
"تنفيذ": "Run",
"تنفيذ ونقل {0} ملف": "Move {0} file(s)",
"جارٍ البحث عن الملفات المتطابقة...": "Searching for identical files...",
"جارٍ الفحص...": "Scanning...",
"جارٍ الفحص... {0} ملف": "Scanning... {0} files",
"جارٍ تحليل {0} صورة...": "Analyzing {0} images...",
"جارٍ تحليل الصور... {0}/{1}": "Analyzing images... {0}/{1}",
"جارٍ مقارنة الصور...": "Comparing images...",
"جارٍ مقارنة المحتوى... {0}/{1}": "Comparing contents... {0}/{1}",
"حدد الصور اللي بدك تنقلها أولاً.": "Select the images you want to move first.",
"حدد الملفات اللي بدك تحذفها.": "Select the files you want to delete.",
"حدد النسخ أولاً (أو اكبس «حدد النسخ الزايدة»).": "Select copies first (or press “Select extra copies”).",
"حذف النوع «{0}»؟": "Delete type “{0}”?",
"حسب الحجم  (صغير / متوسط / كبير / ضخم)": "By size  (small / medium / large / huge)",
"حسب اللاحقة فقط  (JPG / PDF / MP4 ...)": "By extension only  (JPG / PDF / MP4 ...)",
"حسب النوع بس  (صور / فيديو / مستندات ...)": "By type only  (Images / Video / Documents ...)",
"حسب سنة وشهر التعديل  (2025/03 ...)": "By modified year & month  (2025/03 ...)",
"حول": "About",
"خانات:": "Digits:",
"خيارات عامة": "General",
"درجة التشابه:": "Similarity:",
"رجوع للاسم": "Original name",
"رحلة 001": "Trip 001",
"رحلة {n}": "Trip {n}",
"رقم": "Number",
"شكل الاسم الجديد:": "New name pattern:",
"صغير (أقل من 1 ميغا)": "Small (under 1 MB)",
"صغيرة": "lowercase",
"صور": "Images",
"صور 2025-01-31 001": "2025-01-31 001",
"صور مكررة": "Duplicate images",
"ضخم (أكبر من 1 غيغا)": "Huge (over 1 GB)",
"ضيف:": "Insert:",
"طريقة التنظيم الافتراضية:": "Default organize mode:",
"طريقة التنظيم:": "Organize by:",
"غير موجود: {0}": "Not found: {0}",
"غيغا": "GB",
"فتح الملف": "Open file",
"فتح مكان الملف": "Open file location",
"قوالب جاهزة:": "Presets:",
"كبير (100 ميغا - 1 غيغا)": "Large (100 MB - 1 GB)",
"كبيرة": "UPPERCASE",
"كل الأحجام": "All sizes",
"كل التواريخ": "All dates",
"كل الصور": "All images",
"كل الملفات ({0})": "All files ({0})",
"كل الملفات بمكانها الصحيح، ما في شي ينقل.": "All files are already in place — nothing to move.",
"كل شي منظم، ما في ملفات بدها نقل 👌": "Everything is organized — nothing to move 👌",
"كيلو": "KB",
"لا توجد عملية للتراجع عنها.": "Nothing to undo.",
"لاحقة صغيرة (.JPG ← .jpg)": "Lowercase extension (.JPG → .jpg)",
"ما في صور متشابهة 👌": "No similar images 👌",
"ما في ملفات محددة.": "No files selected.",
"ما في ملفات مكررة بهالمجلد 👌": "No duplicate files in this folder 👌",
"متأكد؟ رح ينقل {0} ملف.\n(بتقدر تتراجع بعدين)": "Are you sure? {0} file(s) will be moved.\n(You can undo later)",
"متشابهة": "Similar",
"متشابهة كتير": "Very similar",
"متل ما هي": "Keep",
"متوسط (1-100 ميغا)": "Medium (1-100 MB)",
"مجموعة {0}  —  {1} صور  •  بتوفّر {2}": "Group {0}  —  {1} images  •  saves {2}",
"مجموعة {0} — {1} نسخ  ({2} للنسخة)": "Group {0} — {1} copies  ({2} each)",
"معاينة (المجلد ← عدد الملفات):": "Preview (folder ← number of files):",
"معاينة:": "Preview:",
"معروض أول 300 مجموعة.": "Showing the first 300 groups.",
"ملفات متطابقة 100% (نفس المحتوى حتى لو الاسم مختلف)": "100% identical files (same content even if the name differs)",
"ملفات مكررة": "Duplicate files",
"منظّم الملفات": "File Organizer",
"ميغا": "MB",
"نسخ المسار": "Copy path",
"نسخة": "Copy",
"نفس الصورة (مكررة)": "Same image (duplicate)",
"نقل": "Move",
"نقل {0} صورة ({1}) إلى:\n{2} ؟\n(بتقدر تتراجع بعدين)": "Move {0} image(s) ({1}) to:\n{2}?\n(You can undo later)",
"نقل {0} ملف ({1})\nإلى:\n{2} ؟": "Move {0} file(s) ({1})\nto:\n{2}?",
"نقل {0} ملف ({1}) لسلة المحذوفات؟\nفيك ترجعهن من سلة المحذوفات بالويندوز.": "Move {0} file(s) ({1}) to the Recycle Bin?\nYou can restore them from the Windows Recycle Bin.",
"نقل {0} ملف إلى «ملفات مكررة»؟": "Move {0} file(s) to “Duplicate files”?",
"نقل المحدد إلى...": "Move selected to...",
"نقل كل المعروض إلى...": "Move all shown to...",
"نموذج: منظّم الملفات من GraphicWO  123": "Sample: File Organizer by GraphicWO  123",
"نوع جديد": "New type",
"نوع جديد {0}": "New type {0}",
"هالميزة بتحتاج مكتبة Pillow.\nهي موجودة جوّا نسخة الـ EXE، أو نزّلها بالأمر:\npip install pillow": "This feature needs the Pillow library.\nIt's included in the EXE version, or install it with:\npip install pillow",
"ℹ حول": "ℹ About",
"↩ تراجع (Ctrl+Z)": "↩ Undo (Ctrl+Z)",
"↺ الافتراضي": "↺ Defaults",
"▶ فتح الملف": "▶ Open file",
"⚙ الإعدادات": "⚙ Settings",
"✏ إعادة تسمية (F2)": "✏ Rename (F2)",
"✏ تسمية {0} ملف": "✏ Rename {0} file(s)",
"✔ حدد المكرر تلقائياً (خلّي الأفضل)": "✔ Auto-select duplicates (keep the best)",
"✔ حدد النسخ الزايدة (خلّي الأصلية)": "✔ Select extra copies (keep the original)",
"✖ إلغاء التحديد": "✖ Clear selection",
"✨ تنظيم تلقائي...": "✨ Auto organize...",
"➕ نوع جديد": "➕ New type",
"⭐ الأصلية (الأقدم)": "⭐ Original (oldest)",
"⭐ الأفضل  •  ": "⭐ Best  •  ",
"⭐ حسب النوع ثم اللاحقة  (صور/JPG ، صور/PNG ، فيديو/MP4 ، مستندات/PDF ...)": "⭐ By type, then extension  (Images/JPG, Images/PNG, Video/MP4, Documents/PDF ...)",
"👁 المعاينة": "👁 Preview",
"💾 حفظ": "💾 Save",
"📁 اختيار مجلد": "📁 Choose folder",
"📁 الكل": "📁 All",
"📂 مكانه": "📂 Location",
"📌 بدون المجلدات الفرعية": "📌 Subfolders are never touched",
"📑 الملفات المكررة": "📑 Duplicate files",
"📦 انقل المحدد إلى...": "📦 Move selected to...",
"📦 انقل المحدد لمجلد «صور مكررة»": "📦 Move selected to “Duplicate images”",
"📦 انقل المحدد لمجلد «ملفات مكررة»": "📦 Move selected to “Duplicate files”",
"📦 نقل المحدد...": "📦 Move selected...",
"🔍 ابحث": "🔍 Search",
"🔍 فحص": "🔍 Scan",
"🖼 الصور المتشابهة": "🖼 Similar images",
"🗑 حذف (Del)": "🗑 Delete (Del)",
"🗑 حذف النوع": "🗑 Delete type",
"🗑 لسلة المحذوفات": "🗑 To Recycle Bin",
"فيديو": "Videos",
"صوت": "Audio",
"مستندات": "Documents",
"أرشيف": "Archives",
"برامج": "Programs",
"كود": "Code",
"خطوط": "Fonts",
"أزرق ليلي": "Night blue",
"فاتح": "Light",
"بنفسجي": "Purple",
"برتقالي": "Orange",
"وردي": "Pink",
"أخضر GraphicWO": "GraphicWO green",
"اللغة:": "Language:",
"أسود": "Black",
"أبيض": "White",
"رح يعيد البرنامج التشغيل لتتغيّر اللغة.": "The app will restart to change the language.",
"🎉 في تحديث جديد": "🎉 Update available",
"في نسخة جديدة من البرنامج ({0}).\nنسختك: {1}\n\n{2}\n\nبدك تنزّلها هلق؟": "A new version is available ({0}).\nYour version: {1}\n\n{2}\n\nDownload it now?"
},
"fr": {
"🎉 في تحديث جديد": "🎉 Mise à jour disponible",
"في نسخة جديدة من البرنامج ({0}).\nنسختك: {1}\n\n{2}\n\nبدك تنزّلها هلق؟": "Une nouvelle version est disponible ({0}).\nVotre version : {1}\n\n{2}\n\nLa télécharger maintenant ?",
"\n\nفشل نقل {0} ملف:\n": "\n\nÉchec du déplacement de {0} fichier(s) :\n",
"\n\nما انحذفوا ({0}):\n": "\n\nNon supprimés ({0}) :\n",
"   |   المحدد: {0} ملف ({1})": "   |   Sélection : {0} fichier(s) ({1})",
"   الرقم يبدأ من:": "   Numéro de départ :",
"  —  الجدول يعرض أول {0} فقط، لكن «نقل كل المعروض» يشمل الكل": "  —  le tableau n'affiche que les {0} premiers, mais « Déplacer tout l'affiché » inclut tout",
"1 – 10 ميغا": "1 – 10 Mo",
"10 – 100 ميغا": "10 – 100 Mo",
"100 ميغا – 1 غيغا": "100 Mo – 1 Go",
"{0}   ←   {1} ملف": "{0}   ←   {1} fichier(s)",
"{0}  ({1:,} بايت)": "{0}  ({1:,} octets)",
"{0}  •  الإصدار {1}": "{0}  •  version {1}",
"{0} بايت": "{0} o",
"{0} مجموعة  •  {1} صورة متشابهة  •  المحدد: {2} ({3})": "{0} groupe(s)  •  {1} images similaires  •  sélection : {2} ({3})",
"{0} مجموعة  •  {1} نسخة زايدة  •  بتوفّر {2}": "{0} groupe(s)  •  {1} copies en trop  •  libère {2}",
"{date} بياخد تاريخ التصوير من الكاميرا للصور، وإلا تاريخ التعديل": "{date} utilise la date de prise de vue pour les photos, sinon la date de modification",
"آخر 30 يوم": "30 derniers jours",
"آخر 7 أيام": "7 derniers jours",
"آخر تعديل": "Modifié",
"آخر سنة": "Dernière année",
"أخرى": "Autres",
"أصغر من 1 ميغا": "Moins de 1 Mo",
"أقدم من سنة": "Plus d'un an",
"أقصى عدد ملفات يُعرض بالجدول:": "Nombre max. de fichiers affichés :",
"أكبر من 1 غيغا": "Plus de 1 Go",
"أول حرف كبير": "Majuscule initiale",
"إرجاع الأنواع للوضع الافتراضي؟": "Restaurer les types par défaut ?",
"إظهار لوحة المعاينة": "Afficher le panneau d'aperçu",
"إعادة تسمية": "Renommage",
"إعادة تسمية {0} ملف ({1})": "Renommer {0} fichier(s) ({1})",
"إعادة تسمية {0} ملف؟\n(بتقدر تتراجع بعدين)": "Renommer {0} fichier(s) ?\n(Vous pourrez annuler)",
"إعادة تسمية جماعية": "Renommage par lot",
"إعادة تسمية...": "Renommer...",
"إغلاق": "Fermer",
"إلغاء": "Annuler",
"اختار درجة التشابه واكبس «ابحث».": "Choisissez un niveau de similarité puis « Rechercher ».",
"اختار ملف لتشوف معاينته": "Sélectionnez un fichier pour l'aperçu",
"اختار نوع من القائمة وعدّل لواحقه (افصل بينها بمسافة). الملفات اللي لاحقتها مو موجودة بتروح لـ «أخرى».": "Choisissez un type et modifiez ses extensions (séparées par des espaces). Les autres fichiers vont dans « Autres ».",
"اختر المجلد": "Choisir le dossier",
"اختر المجلد الذي سيتم النقل إليه": "Choisir le dossier de destination",
"اختر مجلداً ثم اضغط «فحص».": "Choisissez un dossier, puis « Analyser ».",
"اختر مجلداً صحيحاً أولاً.": "Choisissez d'abord un dossier valide.",
"اسألني للتأكيد قبل النقل": "Demander confirmation avant de déplacer",
"استبدال:": "Remplacer :",
"اسم الملف": "Nom du fichier",
"اسم النوع (هو اسم المجلد وقت التنظيم):": "Nom du type (nom du dossier lors du rangement) :",
"اسم مجلد الملفات غير المصنفة:": "Dossier des fichiers non classés :",
"افحص مجلداً أولاً.": "Analysez d'abord un dossier.",
"الأبعاد": "Dimensions",
"الأحرف:": "Casse :",
"الألوان:": "Couleurs :",
"الأنواع واللواحق": "Types et extensions",
"الإعدادات": "Paramètres",
"الاسم": "Nom",
"الاسم الجديد": "Nouveau nom",
"الاسم الحالي": "Nom actuel",
"الاسم_001": "nom_001",
"التاريخ": "Date",
"التاريخ (الأقدم أولاً)": "Date (plus ancien d'abord)",
"التاريخ:": "Date :",
"التراجع عن آخر عملية «{0}»؟\n{1} ملف بيرجعوا متل ما كانوا.\n(العملية من: {2})": "Annuler la dernière opération « {0} » ?\n{1} fichier(s) seront restaurés.\n(du : {2})",
"الترتيب الحالي": "Ordre actuel",
"الترقيم حسب:": "Numéroter par :",
"التصنيف": "Catégorie",
"الحجم": "Taille",
"الحجم الكلي": "Taille totale",
"الحجم:": "Taille :",
"الخط «{0}» مو منزّل على الجهاز — رح يستخدم {1} لحد ما تنزّله أو تحطّه بمجلد fonts": "La police « {0} » n'est pas installée — {1} est utilisée en attendant (ou placez-la dans le dossier fonts)",
"الخط:": "Police :",
"الصور المتشابهة": "Images similaires",
"العدد": "Nombre",
"الكل": "Tout",
"اللاحقة": "Extension",
"اللواحق:": "Extensions :",
"المجلد:": "Dossier :",
"المجلدات الجديدة تنعمل داخل:": "Les nouveaux dossiers seront créés dans :",
"المحددة": "sélectionnés",
"المظهر والخط": "Apparence et police",
"المعاينة": "Aperçu",
"المعروض: {0}": "Affiché : {0}",
"المعروض: {0} ملف ({1})": "Affiché : {0} fichier(s) ({1})",
"المعروضة": "affichés",
"المعروضة بس": "Affichées seulement",
"المكان": "Emplacement",
"الملف": "Fichier",
"الملفات المعروضة حالياً فقط ({0})": "Seulement les fichiers affichés ({0})",
"الملفات المكررة": "Fichiers en double",
"الملفات:": "Fichiers :",
"النسبة": "Part",
"النوع": "Type",
"النوع / اللاحقة": "Type / extension",
"الوقت": "Heure",
"اليوم": "Aujourd'hui",
"انحذف {0} ملف لسلة المحذوفات 🗑": "{0} fichier(s) placés dans la corbeille 🗑",
"بحث:": "Recherche :",
"بدون لاحقة": "Sans extension",
"بـ": "par",
"تاريخ الإنشاء": "Créé",
"تاريخ التصوير/التعديل": "Date photo/modif.",
"تجاهل الملفات والمجلدات المخفية": "Ignorer les fichiers et dossiers cachés",
"تسمية": "Renommer",
"تطوير وتصميم: {0}": "Développé et conçu par {0}",
"تطوير: {0}": "par {0}",
"تغيير": "Modifier",
"تم إرجاع {0} ملف ✅": "{0} fichier(s) restaurés ✅",
"تم تحديد {0} ملف": "{0} fichiers sélectionnés",
"تم نسخ مسار {0} ملف 📋": "Chemin de {0} fichier(s) copié 📋",
"تم نقل {0} ملف ✅": "{0} fichier(s) déplacés ✅",
"تمت إعادة تسمية {0} ملف ✅": "{0} fichier(s) renommés ✅",
"تنظيم تلقائي": "Rangement automatique",
"تنفيذ": "Exécuter",
"تنفيذ ونقل {0} ملف": "Déplacer {0} fichier(s)",
"جارٍ البحث عن الملفات المتطابقة...": "Recherche de fichiers identiques...",
"جارٍ الفحص...": "Analyse...",
"جارٍ الفحص... {0} ملف": "Analyse... {0} fichiers",
"جارٍ تحليل {0} صورة...": "Analyse de {0} images...",
"جارٍ تحليل الصور... {0}/{1}": "Analyse des images... {0}/{1}",
"جارٍ مقارنة الصور...": "Comparaison des images...",
"جارٍ مقارنة المحتوى... {0}/{1}": "Comparaison du contenu... {0}/{1}",
"حدد الصور اللي بدك تنقلها أولاً.": "Sélectionnez d'abord les images à déplacer.",
"حدد الملفات اللي بدك تحذفها.": "Sélectionnez les fichiers à supprimer.",
"حدد النسخ أولاً (أو اكبس «حدد النسخ الزايدة»).": "Sélectionnez d'abord les copies (ou « Sélectionner les copies en trop »).",
"حذف النوع «{0}»؟": "Supprimer le type « {0} » ?",
"حسب الحجم  (صغير / متوسط / كبير / ضخم)": "Par taille  (petit / moyen / grand / énorme)",
"حسب اللاحقة فقط  (JPG / PDF / MP4 ...)": "Par extension seulement  (JPG / PDF / MP4 ...)",
"حسب النوع بس  (صور / فيديو / مستندات ...)": "Par type seulement  (Images / Vidéos / Documents ...)",
"حسب سنة وشهر التعديل  (2025/03 ...)": "Par année et mois de modification  (2025/03 ...)",
"حول": "À propos",
"خانات:": "Chiffres :",
"خيارات عامة": "Général",
"درجة التشابه:": "Similarité :",
"رجوع للاسم": "Nom d'origine",
"رحلة 001": "Voyage 001",
"رحلة {n}": "Voyage {n}",
"رقم": "Numéro",
"شكل الاسم الجديد:": "Modèle du nouveau nom :",
"صغير (أقل من 1 ميغا)": "Petit (moins de 1 Mo)",
"صغيرة": "minuscules",
"صور": "Images",
"صور 2025-01-31 001": "2025-01-31 001",
"صور مكررة": "Images en double",
"ضخم (أكبر من 1 غيغا)": "Énorme (plus de 1 Go)",
"ضيف:": "Insérer :",
"طريقة التنظيم الافتراضية:": "Mode de rangement par défaut :",
"طريقة التنظيم:": "Ranger par :",
"غير موجود: {0}": "Introuvable : {0}",
"غيغا": "Go",
"فتح الملف": "Ouvrir le fichier",
"فتح مكان الملف": "Ouvrir l'emplacement",
"قوالب جاهزة:": "Modèles :",
"كبير (100 ميغا - 1 غيغا)": "Grand (100 Mo - 1 Go)",
"كبيرة": "MAJUSCULES",
"كل الأحجام": "Toutes les tailles",
"كل التواريخ": "Toutes les dates",
"كل الصور": "Toutes les images",
"كل الملفات ({0})": "Tous les fichiers ({0})",
"كل الملفات بمكانها الصحيح، ما في شي ينقل.": "Tous les fichiers sont déjà rangés — rien à déplacer.",
"كل شي منظم، ما في ملفات بدها نقل 👌": "Tout est rangé — rien à déplacer 👌",
"كيلو": "Ko",
"لا توجد عملية للتراجع عنها.": "Rien à annuler.",
"لاحقة صغيرة (.JPG ← .jpg)": "Extension en minuscules (.JPG → .jpg)",
"ما في صور متشابهة 👌": "Aucune image similaire 👌",
"ما في ملفات محددة.": "Aucun fichier sélectionné.",
"ما في ملفات مكررة بهالمجلد 👌": "Aucun doublon dans ce dossier 👌",
"متأكد؟ رح ينقل {0} ملف.\n(بتقدر تتراجع بعدين)": "Confirmer ? {0} fichier(s) seront déplacés.\n(Vous pourrez annuler)",
"متشابهة": "Similaires",
"متشابهة كتير": "Très similaires",
"متل ما هي": "Inchangée",
"متوسط (1-100 ميغا)": "Moyen (1-100 Mo)",
"مجموعة {0}  —  {1} صور  •  بتوفّر {2}": "Groupe {0}  —  {1} images  •  libère {2}",
"مجموعة {0} — {1} نسخ  ({2} للنسخة)": "Groupe {0} — {1} copies  ({2} chacune)",
"معاينة (المجلد ← عدد الملفات):": "Aperçu (dossier ← nombre de fichiers) :",
"معاينة:": "Aperçu :",
"معروض أول 300 مجموعة.": "Affichage des 300 premiers groupes.",
"ملفات متطابقة 100% (نفس المحتوى حتى لو الاسم مختلف)": "Fichiers 100 % identiques (même contenu, même si le nom diffère)",
"ملفات مكررة": "Fichiers en double",
"منظّم الملفات": "Organiseur de fichiers",
"ميغا": "Mo",
"نسخ المسار": "Copier le chemin",
"نسخة": "Copie",
"نفس الصورة (مكررة)": "Même image (doublon)",
"نقل": "Déplacement",
"نقل {0} صورة ({1}) إلى:\n{2} ؟\n(بتقدر تتراجع بعدين)": "Déplacer {0} image(s) ({1}) vers :\n{2} ?\n(Vous pourrez annuler)",
"نقل {0} ملف ({1})\nإلى:\n{2} ؟": "Déplacer {0} fichier(s) ({1})\nvers :\n{2} ?",
"نقل {0} ملف ({1}) لسلة المحذوفات؟\nفيك ترجعهن من سلة المحذوفات بالويندوز.": "Placer {0} fichier(s) ({1}) dans la corbeille ?\nVous pourrez les restaurer depuis la corbeille Windows.",
"نقل {0} ملف إلى «ملفات مكررة»؟": "Déplacer {0} fichier(s) vers « Fichiers en double » ?",
"نقل المحدد إلى...": "Déplacer la sélection vers...",
"نقل كل المعروض إلى...": "Déplacer tout l'affiché vers...",
"نموذج: منظّم الملفات من GraphicWO  123": "Exemple : Organiseur de fichiers GraphicWO  123",
"نوع جديد": "Nouveau type",
"نوع جديد {0}": "Nouveau type {0}",
"هالميزة بتحتاج مكتبة Pillow.\nهي موجودة جوّا نسخة الـ EXE، أو نزّلها بالأمر:\npip install pillow": "Cette fonction nécessite la bibliothèque Pillow.\nElle est incluse dans la version EXE, ou installez-la avec :\npip install pillow",
"ℹ حول": "ℹ À propos",
"↩ تراجع (Ctrl+Z)": "↩ Annuler (Ctrl+Z)",
"↺ الافتراضي": "↺ Par défaut",
"▶ فتح الملف": "▶ Ouvrir",
"⚙ الإعدادات": "⚙ Paramètres",
"✏ إعادة تسمية (F2)": "✏ Renommer (F2)",
"✏ تسمية {0} ملف": "✏ Renommer {0} fichier(s)",
"✔ حدد المكرر تلقائياً (خلّي الأفضل)": "✔ Sélection auto des doublons (garder le meilleur)",
"✔ حدد النسخ الزايدة (خلّي الأصلية)": "✔ Sélectionner les copies en trop (garder l'original)",
"✖ إلغاء التحديد": "✖ Désélectionner",
"✨ تنظيم تلقائي...": "✨ Ranger automatiquement...",
"➕ نوع جديد": "➕ Nouveau type",
"⭐ الأصلية (الأقدم)": "⭐ Original (le plus ancien)",
"⭐ الأفضل  •  ": "⭐ Meilleure  •  ",
"⭐ حسب النوع ثم اللاحقة  (صور/JPG ، صور/PNG ، فيديو/MP4 ، مستندات/PDF ...)": "⭐ Par type puis extension  (Images/JPG, Images/PNG, Vidéos/MP4, Documents/PDF ...)",
"👁 المعاينة": "👁 Aperçu",
"💾 حفظ": "💾 Enregistrer",
"📁 اختيار مجلد": "📁 Choisir un dossier",
"📁 الكل": "📁 Tout",
"📂 مكانه": "📂 Emplacement",
"📌 بدون المجلدات الفرعية": "📌 Les sous-dossiers ne sont jamais touchés",
"📑 الملفات المكررة": "📑 Fichiers en double",
"📦 انقل المحدد إلى...": "📦 Déplacer la sélection vers...",
"📦 انقل المحدد لمجلد «صور مكررة»": "📦 Déplacer vers « Images en double »",
"📦 انقل المحدد لمجلد «ملفات مكررة»": "📦 Déplacer vers « Fichiers en double »",
"📦 نقل المحدد...": "📦 Déplacer...",
"🔍 ابحث": "🔍 Rechercher",
"🔍 فحص": "🔍 Analyser",
"🖼 الصور المتشابهة": "🖼 Images similaires",
"🗑 حذف (Del)": "🗑 Supprimer (Suppr)",
"🗑 حذف النوع": "🗑 Supprimer le type",
"🗑 لسلة المحذوفات": "🗑 Vers la corbeille",
"فيديو": "Vidéos",
"صوت": "Audio",
"مستندات": "Documents",
"أرشيف": "Archives",
"برامج": "Programmes",
"كود": "Code",
"خطوط": "Polices",
"أزرق ليلي": "Bleu nuit",
"فاتح": "Clair",
"بنفسجي": "Violet",
"برتقالي": "Orange",
"وردي": "Rose",
"أخضر GraphicWO": "Vert GraphicWO",
"اللغة:": "Langue :",
"أسود": "Noir",
"أبيض": "Blanc",
"رح يعيد البرنامج التشغيل لتتغيّر اللغة.": "L'application va redémarrer pour changer de langue."
}
}


def T(s):
    if LANG == "ar":
        return s
    return TR.get(LANG, {}).get(s, s)


APP_NAME = T("منظّم الملفات")
APP_VERSION = "1.1"
UPDATE_URL = "https://graphicwo-studio.github.io/version.json"
DOWNLOAD_URL = "https://github.com/GraphicWO-Studio/graphicwo-studio.github.io/releases/download/organizer-latest/GraphicWO_Organizer.exe"
DEV_NAME = "GraphicWO"
DEV_LINK = "https://kick.com/graphicwo"
APP_TITLE = f"{APP_NAME}  —  {DEV_NAME}"

HOME = os.path.expanduser("~")
UNDO_FILE = os.path.join(HOME, ".graphicwo_organizer_undo.json")
SETTINGS_FILE = os.path.join(HOME, ".graphicwo_organizer_settings.json")

KB, MB, GB = 1024, 1024 ** 2, 1024 ** 3

# ثيمات الألوان (بتختارها من الإعدادات)
_K = ("BG", "PANEL", "FIELD", "LINE", "FG", "MUTED", "ACCENT", "ACCENT_FG", "ACCENT_HOVER",
      "SEL", "SEL_FG", "HEADER", "BTN", "BTN_HOVER", "HEAD", "ODD")
THEMES = {
    "أزرق ليلي": ("#0f1420", "#151c2c", "#1b2438", "#2a3654", "#e6ebf5", "#8d9bb8", "#4f8cff", "#ffffff",
                  "#6ea0ff", "#2c4a86", "#ffffff", "#0a0e17", "#1e2840", "#28365a", "#1a2236", "#131a29"),
    "فاتح": ("#f3f5f9", "#ffffff", "#ffffff", "#d5dbe6", "#1d2433", "#6b7487", "#2563eb", "#ffffff",
             "#3b76f0", "#cfe0ff", "#0f1b3a", "#ffffff", "#e8ecf3", "#dbe2ee", "#eef1f7", "#f7f9fc"),
    "بنفسجي": ("#15111f", "#1c1729", "#241d35", "#3a2f55", "#efe9fb", "#a397c2", "#a855f7", "#ffffff",
               "#bf7bff", "#5b2d91", "#ffffff", "#0f0b17", "#271f3a", "#35294f", "#221a33", "#1a1526"),
    "برتقالي": ("#141210", "#1c1915", "#25211b", "#3d352a", "#f5efe6", "#b3a58f", "#ff8a3d", "#1a0f05",
                "#ffa366", "#7a3f17", "#ffffff", "#0d0b09", "#2a241c", "#3a3126", "#221e18", "#191612"),
    "وردي": ("#18111a", "#201722", "#2a1e2d", "#45304a", "#fbeaf6", "#c19bb7", "#ff4fa3", "#ffffff",
             "#ff78ba", "#7d2457", "#ffffff", "#100b12", "#2c1f30", "#3d2b42", "#25192a", "#1c141f"),
    "أسود": ("#000000", "#0a0a0a", "#141414", "#2e2e2e", "#ffffff", "#9a9a9a", "#ffffff", "#000000",
             "#d9d9d9", "#3a3a3a", "#ffffff", "#000000", "#1a1a1a", "#2a2a2a", "#111111", "#070707"),
    "أبيض": ("#ffffff", "#ffffff", "#ffffff", "#d4d4d4", "#000000", "#6b6b6b", "#000000", "#ffffff",
             "#2b2b2b", "#e6e6e6", "#000000", "#ffffff", "#f0f0f0", "#e2e2e2", "#f5f5f5", "#fafafa"),
    "أخضر GraphicWO": ("#0b120d", "#111c15", "#162419", "#23402b", "#e8f5ea", "#8fb39a", "#7ee81f", "#06110a",
                       "#a4ff4f", "#2b6e2f", "#ffffff", "#050a06", "#1b2e20", "#24402b", "#1a2c1f", "#0f1912"),
}
DEFAULT_THEME = "أزرق ليلي"


def set_theme(name):
    globals().update(dict(zip(_K, THEMES.get(name, THEMES[DEFAULT_THEME]))))


set_theme(DEFAULT_THEME)

DEFAULT_CATEGORIES = {
    "صور": "jpg jpeg png gif bmp webp tif tiff heic heif svg ico raw cr2 nef arw dng psd ai jfif",
    "فيديو": "mp4 mkv avi mov wmv flv webm m4v 3gp mpeg mpg vob mts m2ts",
    "صوت": "mp3 wav flac aac ogg m4a wma opus amr mid midi",
    "مستندات": "pdf doc docx odt rtf txt md xls xlsx xlsm csv ods ppt pptx odp epub",
    "أرشيف": "zip rar 7z tar gz bz2 xz tgz iso cab",
    "برامج": "exe msi apk xapk dmg pkg deb rpm appimage bat cmd appx msix jar",
    "كود": "py js ts jsx tsx html htm css scss json xml yml yaml java c cpp h hpp cs php sql sh ps1 go rs kt swift ipynb",
    "خطوط": "ttf otf woff woff2 fon",
}
DEFAULT_CATEGORIES = {T(k): v for k, v in DEFAULT_CATEGORIES.items()}
DEFAULT_SETTINGS = {
    "categories": DEFAULT_CATEGORIES,
    "recursive": False,
    "skip_hidden": True,
    "confirm": True,
    "max_rows": 5000,
    "default_mode": "cat_ext",
    "ver": 2,
    "other_name": T("أخرى"),
    "last_folder": "",
    "theme": DEFAULT_THEME,
    "show_preview": True,
    "font": "GE SS Two",
    "recent": [],
    "lang": LANG,
}
NOEXT = T("بدون لاحقة")
SKIP_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}
ICONS = {"صور": "🖼", "فيديو": "🎬", "صوت": "🎵", "مستندات": "📄", "أرشيف": "🗜",
         "برامج": "⚙", "كود": "💻", "خطوط": "🔤"}
ICONS.update({T(k): v for k, v in list(ICONS.items())})

SIZE_FILTERS = [
    (T("كل الأحجام"), 0, None),
    (T("أصغر من 1 ميغا"), 0, MB),
    (T("1 – 10 ميغا"), MB, 10 * MB),
    (T("10 – 100 ميغا"), 10 * MB, 100 * MB),
    (T("100 ميغا – 1 غيغا"), 100 * MB, GB),
    (T("أكبر من 1 غيغا"), GB, None),
]
ORGANIZE_MODES = [
    ("cat_ext", T("⭐ حسب النوع ثم اللاحقة  (صور/JPG ، صور/PNG ، فيديو/MP4 ، مستندات/PDF ...)")),
    ("cat", T("حسب النوع بس  (صور / فيديو / مستندات ...)")),
    ("ext", T("حسب اللاحقة فقط  (JPG / PDF / MP4 ...)")),
    ("size", T("حسب الحجم  (صغير / متوسط / كبير / ضخم)")),
    ("date", T("حسب سنة وشهر التعديل  (2025/03 ...)")),
]

LOGO_B64 = "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"
AVATAR_B64 = "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"
ICON_B64 = "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"
AVATAR_SMALL_B64 = "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"



# ------------------------------------------------------------------ الإعدادات

class Settings:
    def __init__(self):
        self.data = json.loads(json.dumps(DEFAULT_SETTINGS))
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as fh:
                self.data.update(json.load(fh))
        except (OSError, ValueError):
            pass
        if self.data.get("ver", 1) < 2:  # ترقية: الافتراضي صار نوع ← لاحقة
            self.data["default_mode"] = "cat_ext"
            self.data["ver"] = 2
        self.rebuild()

    def rebuild(self):
        self.ext_map = {}
        for cat, exts in self.data["categories"].items():
            for e in exts.replace(",", " ").split():
                self.ext_map[e.lower().lstrip(".")] = cat

    def __getitem__(self, k):
        return self.data[k]

    def __setitem__(self, k, v):
        self.data[k] = v

    def save(self):
        self.rebuild()
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, ensure_ascii=False, indent=1)
        except OSError:
            pass


S = Settings()


# ------------------------------------------------------------------ المنطق

def human(n):
    for unit, size in ((T("غيغا"), GB), (T("ميغا"), MB), (T("كيلو"), KB)):
        if n >= size:
            return f"{n / size:.1f} {unit}"
    return T("{0} بايت").format(n)


def size_bucket(n):
    if n < MB:
        return T("صغير (أقل من 1 ميغا)")
    if n < 100 * MB:
        return T("متوسط (1-100 ميغا)")
    if n < GB:
        return T("كبير (100 ميغا - 1 غيغا)")
    return T("ضخم (أكبر من 1 غيغا)")


def file_info(path):
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower().lstrip(".")
    st = os.stat(path)
    return {"path": path, "name": name, "ext": ext.upper() if ext else NOEXT,
            "cat": S.ext_map.get(ext, S["other_name"]), "size": st.st_size, "mtime": st.st_mtime}


def scan_folder(root, recursive, progress=None):
    skip_hidden = S["skip_hidden"]
    files = []
    if recursive:
        walker = os.walk(root, onerror=lambda e: None)
    else:
        try:
            walker = [(root, [], os.listdir(root))]
        except OSError:
            walker = []
    for dirpath, dirnames, filenames in walker:
        dirnames[:] = [d for d in dirnames if d != "$RECYCLE.BIN" and not (skip_hidden and d.startswith("."))]
        for fn in filenames:
            if fn.lower() in SKIP_NAMES or (skip_hidden and fn.startswith(".")):
                continue
            p = os.path.join(dirpath, fn)
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            try:
                files.append(file_info(p))
            except OSError:
                continue
            if progress and len(files) % 500 == 0:
                progress(len(files))
    return files


def target_dir(f, root, mode):
    if mode == "cat":
        return os.path.join(root, f["cat"])
    if mode == "cat_ext":
        return os.path.join(root, f["cat"], f["ext"])
    if mode == "ext":
        return os.path.join(root, f["ext"])
    if mode == "size":
        return os.path.join(root, size_bucket(f["size"]))
    if mode == "date":
        d = datetime.fromtimestamp(f["mtime"])
        return os.path.join(root, f"{d.year}", f"{d.month:02d}")
    raise ValueError(mode)


def plan_organize(files, root, mode):
    plan = []
    for f in files:
        d = target_dir(f, root, mode)
        if os.path.normcase(os.path.dirname(f["path"])) != os.path.normcase(d):
            plan.append((f["path"], d))
    return plan


def unique_path(dest_dir, name):
    base, ext = os.path.splitext(name)
    candidate = os.path.join(dest_dir, name)
    i = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_dir, f"{base} ({i}){ext}")
        i += 1
    return candidate


def execute_moves(plan):
    moved, created, errors = [], [], []
    for src, dest_dir in plan:
        try:
            if not os.path.isdir(dest_dir):
                d = dest_dir
                while d and not os.path.isdir(d):
                    created.append(d)
                    d = os.path.dirname(d)
                os.makedirs(dest_dir, exist_ok=True)
            dst = unique_path(dest_dir, os.path.basename(src))
            shutil.move(src, dst)
            moved.append((src, dst))
        except Exception as e:  # noqa
            errors.append(f"{os.path.basename(src)}: {e}")
    return moved, created, errors


def _read_undo():
    try:
        with open(UNDO_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return []
    if isinstance(data, dict):  # صيغة قديمة
        data = [data] if data.get("moved") else []
    return [op for op in data if op.get("moved")]


def _write_undo(ops):
    try:
        with open(UNDO_FILE, "w", encoding="utf-8") as fh:
            json.dump(ops[-30:], fh, ensure_ascii=False)
    except OSError:
        pass


def save_undo(moved, created, label=T("نقل")):
    ops = _read_undo()
    ops.append({"time": datetime.now().isoformat(timespec="seconds"), "label": label,
                "moved": moved, "created": created})
    _write_undo(ops)


def load_undo():
    ops = _read_undo()
    return ops[-1] if ops else None


def undo_count():
    return len(_read_undo())


def undo_last():
    ops = _read_undo()
    if not ops:
        return 0, [T("لا توجد عملية للتراجع عنها.")]
    data = ops.pop()
    ok, errors = 0, []
    for src, dst in reversed(data["moved"]):
        try:
            if not os.path.exists(dst):
                errors.append(T("غير موجود: {0}").format(os.path.basename(dst)))
                continue
            os.makedirs(os.path.dirname(src), exist_ok=True)
            back = src if not os.path.exists(src) else unique_path(os.path.dirname(src), os.path.basename(src))
            shutil.move(dst, back)
            ok += 1
        except Exception as e:  # noqa
            errors.append(f"{os.path.basename(dst)}: {e}")
    for d in sorted(data.get("created", []), key=len, reverse=True):
        try:
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
        except OSError:
            pass
    _write_undo(ops)
    return ok, errors


# ------------------------------------------------------------------ أدوات إضافية

def send_to_trash(paths):
    """نقل لسلة المحذوفات (ويندوز). يرجع (عدد الناجح، أخطاء)."""
    if not paths:
        return 0, []
    if sys.platform.startswith("win"):
        try:
            import ctypes
            from ctypes import wintypes

            class SHFILEOPSTRUCTW(ctypes.Structure):
                _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT),
                            ("pFrom", ctypes.c_void_p), ("pTo", ctypes.c_void_p),
                            ("fFlags", ctypes.c_ushort), ("fAnyOperationsAborted", wintypes.BOOL),
                            ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", ctypes.c_void_p)]
            ok, errors = 0, []
            for i in range(0, len(paths), 200):
                chunk = [os.path.abspath(p) for p in paths[i:i + 200]]
                text = "\0".join(chunk) + "\0\0"
                buf = (ctypes.c_wchar * len(text))(*text)
                op = SHFILEOPSTRUCTW()
                op.wFunc = 3  # FO_DELETE
                op.pFrom = ctypes.cast(buf, ctypes.c_void_p).value
                op.fFlags = 0x0040 | 0x0010 | 0x0400 | 0x0004  # ALLOWUNDO|NOCONFIRMATION|NOERRORUI|SILENT
                r = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
                done = sum(1 for p in chunk if not os.path.exists(p))
                ok += done
                if r != 0 or done < len(chunk):
                    errors += [os.path.basename(p) for p in chunk if os.path.exists(p)]
            return ok, errors
        except Exception as e:  # noqa
            return 0, [str(e)]
    # أنظمة تانية: gio / مجلد سلة محلي
    ok, errors = 0, []
    for p in paths:
        try:
            if shutil.which("gio") and subprocess.call(["gio", "trash", p]) == 0:
                ok += 1
                continue
            trash = os.path.join(HOME, ".local", "share", "Trash", "files")
            os.makedirs(trash, exist_ok=True)
            shutil.move(p, unique_path(trash, os.path.basename(p)))
            ok += 1
        except Exception as e:  # noqa
            errors.append(f"{os.path.basename(p)}: {e}")
    return ok, errors


def file_digest(path, quick=False):
    import hashlib
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        if quick:
            h.update(fh.read(65536))
        else:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest()


def find_exact_duplicates(files, progress=None):
    by_size = {}
    for f in files:
        if f["size"] > 0:
            by_size.setdefault(f["size"], []).append(f)
    cands = [g for g in by_size.values() if len(g) > 1]
    total = sum(len(g) for g in cands)
    done, groups = 0, []
    for g in cands:
        quick = {}
        for f in g:
            try:
                quick.setdefault(file_digest(f["path"], True), []).append(f)
            except OSError:
                pass
            done += 1
            if progress and done % 10 == 0:
                progress(done, total)
        for q in quick.values():
            if len(q) < 2:
                continue
            full = {}
            for f in q:
                try:
                    full.setdefault(file_digest(f["path"]) if f["size"] > 65536 else "same", []).append(f)
                except OSError:
                    pass
            groups += [sorted(x, key=lambda f: f["mtime"]) for x in full.values() if len(x) > 1]
    groups.sort(key=lambda g: -g[0]["size"] * (len(g) - 1))
    return groups


def photo_date(path, mtime):
    """تاريخ التصوير من EXIF إن وُجد، وإلا تاريخ التعديل."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            ex = im.getexif()
            v = None
            try:
                v = ex.get_ifd(0x8769).get(36867)
            except Exception:  # noqa
                pass
            v = v or ex.get(306)
            if v:
                return datetime.strptime(str(v).strip()[:19], "%Y:%m:%d %H:%M:%S")
    except Exception:  # noqa
        pass
    return datetime.fromtimestamp(mtime)


INVALID_CHARS = '<>:"/\\|?*'


def build_new_name(f, idx, opts):
    base, ext = os.path.splitext(f["name"])
    if opts["find"]:
        base = base.replace(opts["find"], opts["replace"])
    num = str(opts["start"] + idx).zfill(opts["digits"])
    pat = opts["pattern"] or "{name}"
    needs_date = "{date}" in pat or "{time}" in pat
    d = photo_date(f["path"], f["mtime"]) if needs_date else None
    new = (pat.replace("{name}", base).replace("{n}", num).replace("{cat}", f["cat"])
           .replace("{ext}", ext.lstrip(".").upper())
           .replace("{date}", d.strftime("%Y-%m-%d") if d else "")
           .replace("{time}", d.strftime("%H-%M-%S") if d else ""))
    if opts["case"] == "lower":
        new = new.lower()
    elif opts["case"] == "upper":
        new = new.upper()
    elif opts["case"] == "title":
        new = new.title()
    ext = ext.lower() if opts["lower_ext"] else ext
    new = "".join("_" if c in INVALID_CHARS else c for c in new).strip().rstrip(".") or base
    return new + ext


DATE_FILTERS = [
    (T("كل التواريخ"), None),
    (T("اليوم"), 1),
    (T("آخر 7 أيام"), 7),
    (T("آخر 30 يوم"), 30),
    (T("آخر سنة"), 365),
    (T("أقدم من سنة"), -365),
]


def open_path(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:  # noqa
        messagebox.showerror(APP_TITLE, str(e))


def reveal_path(path):
    if sys.platform.startswith("win"):
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R", path])
    else:
        open_path(os.path.dirname(path))


# ------------------------------------------------------------------ الخط

PREFERRED_FONT = "GE SS Two"
FALLBACK_FONTS = ("Segoe UI", "Tahoma", "Arial", "DejaVu Sans")
FONT = {"regular": "Segoe UI", "bold": None}


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_private_fonts():
    """يحمّل أي خط .ttf/.otf موجود بمجلد fonts جنب البرنامج (ويندوز) بدون تثبيت."""
    if not sys.platform.startswith("win"):
        return
    dirs = [os.path.join(app_dir(), "fonts")]
    if hasattr(sys, "_MEIPASS"):  # خطوط مدموجة جوّا ملف الـ exe
        dirs.append(os.path.join(sys._MEIPASS, "fonts"))
    try:
        import ctypes
        for d in dirs:
            if os.path.isdir(d):
                for fn in os.listdir(d):
                    if fn.lower().endswith((".ttf", ".otf", ".ttc")):
                        ctypes.windll.gdi32.AddFontResourceExW(os.path.join(d, fn), 0x10, 0)
    except Exception:  # noqa
        pass


def resolve_fonts(root):
    from tkinter import font as tkfont
    fams = set(tkfont.families(root))
    want = S["font"] or PREFERRED_FONT
    regular = None
    for cand in (want, f"{want} Medium", f"{want} Light", f"{want} Regular"):
        if cand in fams:
            regular = cand
            break
    if not regular:
        regular = next((f for f in FALLBACK_FONTS if f in fams), "TkDefaultFont")
    FONT["regular"] = regular
    FONT["bold"] = f"{want} Bold" if f"{want} Bold" in fams and regular.startswith(want) else None
    return regular.startswith(want)


def F(size, bold=False, extra=None):
    if bold and FONT["bold"]:
        t = (FONT["bold"], size)
    else:
        t = (FONT["regular"], size) + (("bold",) if bold else ())
    return t + ((extra,) if extra else ())


# ------------------------------------------------------------------ الصور المتشابهة

SIMILAR_LEVELS = [
    (T("نفس الصورة (مكررة)"), 6),
    (T("متشابهة كتير"), 16),
    (T("متشابهة"), 26),
]
HASHABLE = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "tif", "tiff", "jfif", "ico", "ppm"}


def popcount(x):
    return x.bit_count() if hasattr(x, "bit_count") else bin(x).count("1")


def image_fingerprint(path):
    """بصمة 128 بت (dHash أفقي + عمودي) + الأبعاد."""
    from PIL import Image
    with Image.open(path) as im:
        size = im.size
        im.draft("L", (128, 128))
        g = im.convert("L")
        a = list(g.resize((9, 8)).getdata())
        b = list(g.resize((8, 9)).getdata())
    h = 0
    for r in range(8):
        for c in range(8):
            h = (h << 1) | (a[r * 9 + c] > a[r * 9 + c + 1])
    for r in range(8):
        for c in range(8):
            h = (h << 1) | (b[r * 8 + c] > b[(r + 1) * 8 + c])
    return h, size


def group_similar(items, threshold, progress=None):
    n = len(items)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    hs = [it["hash"] for it in items]
    for i in range(n):
        hi = hs[i]
        for j in range(i + 1, n):
            if popcount(hi ^ hs[j]) <= threshold:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[rj] = ri
        if progress and i % 200 == 0:
            progress(i, n)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(items[i])
    out = [g for g in groups.values() if len(g) > 1]
    for g in out:  # الأفضل أولاً: أعلى دقة ثم أكبر حجم
        g.sort(key=lambda it: (it["w"] * it["h"], it["size"]), reverse=True)
    out.sort(key=lambda g: -sum(it["size"] for it in g[1:]))
    return out


# ------------------------------------------------------------------ المظهر

def apply_theme(root):
    set_theme(S["theme"])
    resolve_fonts(root)
    st = ttk.Style(root)
    st.theme_use("clam")
    font = F(10)
    bold = F(10, True)
    root.configure(bg=BG)
    root.option_add("*Font", font)
    root.option_add("*Menu.background", PANEL)
    root.option_add("*Menu.foreground", FG)
    root.option_add("*Menu.activeBackground", SEL)
    root.option_add("*Menu.activeForeground", SEL_FG)
    root.option_add("*TCombobox*Listbox.background", FIELD)
    root.option_add("*TCombobox*Listbox.foreground", FG)
    root.option_add("*TCombobox*Listbox.selectBackground", SEL)
    root.option_add("*TCombobox*Listbox.selectForeground", SEL_FG)

    st.configure(".", background=BG, foreground=FG, fieldbackground=FIELD, bordercolor=LINE,
                 lightcolor=LINE, darkcolor=LINE, troughcolor=PANEL, focuscolor=ACCENT,
                 selectbackground=SEL, selectforeground=SEL_FG, insertcolor=FG, font=font)
    st.configure("TFrame", background=BG)
    st.configure("Panel.TFrame", background=PANEL)
    st.configure("Header.TFrame", background=HEADER)
    st.configure("TLabel", background=BG, foreground=FG)
    st.configure("Panel.TLabel", background=PANEL, foreground=FG)
    st.configure("PanelMuted.TLabel", background=PANEL, foreground=MUTED)
    st.configure("Muted.TLabel", foreground=MUTED)
    st.configure("Title.TLabel", font=F(11, True), foreground=ACCENT)
    st.configure("Header.TLabel", background=HEADER, foreground=FG)
    st.configure("HeaderMuted.TLabel", background=HEADER, foreground=MUTED, font=F(9))
    st.configure("Status.TLabel", background=HEADER, foreground=MUTED, padding=(10, 4))

    st.configure("TButton", background=BTN, foreground=FG, padding=(10, 5), borderwidth=1)
    st.map("TButton", background=[("active", BTN_HOVER), ("disabled", PANEL)],
           foreground=[("disabled", MUTED)])
    st.configure("Accent.TButton", background=ACCENT, foreground=ACCENT_FG, font=bold)
    st.map("Accent.TButton", background=[("active", ACCENT_HOVER)])
    st.configure("Header.TButton", background=BTN, foreground=FG, padding=(10, 4))
    st.map("Header.TButton", background=[("active", BTN_HOVER)])

    for w in ("TCheckbutton", "TRadiobutton"):
        st.configure(w, background=BG, foreground=FG, indicatorcolor=FIELD)
        st.map(w, indicatorcolor=[("selected", ACCENT)], background=[("active", BG)])
    st.configure("TEntry", fieldbackground=FIELD, foreground=FG, insertcolor=FG)
    st.configure("TSpinbox", fieldbackground=FIELD, foreground=FG, arrowcolor=ACCENT, insertcolor=FG, background=BTN)
    st.configure("TCombobox", fieldbackground=FIELD, foreground=FG, arrowcolor=ACCENT, background=BTN)
    st.map("TCombobox", fieldbackground=[("readonly", FIELD)], foreground=[("readonly", FG)])

    st.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG,
                 rowheight=27, borderwidth=0, font=font)
    st.map("Treeview", background=[("selected", SEL)], foreground=[("selected", SEL_FG)])
    st.configure("Treeview.Heading", background=HEAD, foreground=ACCENT, font=bold, relief="flat")
    st.map("Treeview.Heading", background=[("active", BTN_HOVER)])
    for sb in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
        st.configure(sb, background=BTN_HOVER, troughcolor=PANEL, bordercolor=PANEL,
                     lightcolor=BTN_HOVER, darkcolor=BTN_HOVER, arrowcolor=ACCENT, gripcount=0)
        st.map(sb, background=[("active", ACCENT)])
    st.configure("TNotebook", background=BG, borderwidth=0)
    st.configure("TNotebook.Tab", background=BTN, foreground=MUTED, padding=(14, 6))
    st.map("TNotebook.Tab", background=[("selected", BTN_HOVER)], foreground=[("selected", ACCENT)])
    st.configure("TPanedwindow", background=BG)
    st.configure("Sash", sashthickness=6, background=LINE)


def load_image(b64):
    try:
        return tk.PhotoImage(data=b64)
    except tk.TclError:
        return None


def dark_listbox(parent, **kw):
    return tk.Listbox(parent, bg=FIELD, fg=FG, selectbackground=SEL, selectforeground=SEL_FG,
                      highlightthickness=1, highlightbackground=LINE, highlightcolor=ACCENT,
                      relief="flat", activestyle="none", **kw)


# ------------------------------------------------------------------ التطبيق

IMAGE_EXTS = {"png", "gif", "jpg", "jpeg", "bmp", "webp", "ico", "tif", "tiff", "ppm", "pgm", "jfif"}
TEXT_EXTS = set("txt md csv log ini cfg conf json xml yml yaml py pyw js ts jsx tsx html htm css scss "
                "java c cpp h hpp cs php sql sh bat cmd ps1 go rs kt swift srt vtt env toml".split())


def load_thumb(path, w, h):
    """يرجع (صورة مصغرة، الأبعاد) - يستخدم Pillow إذا موجود، وإلا Tk للـ PNG/GIF."""
    try:
        from PIL import Image, ImageTk
        with Image.open(path) as im:
            size = f"{im.width} × {im.height}"
            im.draft("RGB", (w * 2, h * 2))
            im = im.convert("RGBA")
            im.thumbnail((w, h))
            return ImageTk.PhotoImage(im), size
    except ImportError:
        pass
    except Exception:  # noqa
        return None, None
    try:
        img = tk.PhotoImage(file=path)
        size = f"{img.width()} × {img.height()}"
        k = max(1, -(-img.width() // w), -(-img.height() // h))
        return (img.subsample(k) if k > 1 else img), size
    except tk.TclError:
        return None, None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1400x820")
        self.minsize(1050, 600)
        if sys.platform.startswith("win"):
            try:
                self.state("zoomed")
            except tk.TclError:
                pass
        apply_theme(self)

        self.img_logo = load_image(LOGO_B64)
        self.img_avatar = load_image(AVATAR_B64)
        self.img_avatar_s = load_image(AVATAR_SMALL_B64)
        self.img_icon = load_image(ICON_B64)
        if self.img_icon:
            self.iconphoto(True, self.img_icon)

        self.root_dir = tk.StringVar(value=S["last_folder"])
        self.recursive = tk.BooleanVar(value=S["recursive"])
        self.search = tk.StringVar()
        self.size_filter = tk.StringVar(value=SIZE_FILTERS[0][0])
        self.date_filter = tk.StringVar(value=DATE_FILTERS[0][0])
        self.status = tk.StringVar(value=T("اختر مجلداً ثم اضغط «فحص»."))

        self.files, self.filtered = [], []
        self.sel_cat = self.sel_ext = None
        self.sort_key, self.sort_desc = "size", True

        self.preview_img = None
        self._build()
        self.search.trace_add("write", lambda *_: self.refresh_files())
        self._update_undo_btn()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- بناء الواجهة
    def _build(self):
        # الهيدر: اللوغو + اسم المطور + أزرار
        header = ttk.Frame(self, style="Header.TFrame", padding=(12, 6))
        header.pack(fill="x")
        brand = ttk.Frame(header, style="Header.TFrame")
        brand.pack(side=SR)
        if self.img_avatar_s:
            ttk.Label(brand, image=self.img_avatar_s, style="Header.TLabel").pack(side=SR, padx=(6, 0))
        txt = ttk.Frame(brand, style="Header.TFrame")
        txt.pack(side=SR, padx=6)
        ttk.Label(txt, text=APP_NAME, style="Header.TLabel",
                  font=F(15, True), foreground=ACCENT).pack(anchor=AE)
        ttk.Label(txt, text=T("تطوير: {0}").format(DEV_NAME), style="HeaderMuted.TLabel").pack(anchor=AE)
        if self.img_logo:
            lg = ttk.Label(header, image=self.img_logo, style="Header.TLabel", cursor="hand2")
            lg.pack(side=SL)
            lg.bind("<Button-1>", lambda e: self.about())
        ttk.Button(header, text=T("ℹ حول"), style="Header.TButton", command=self.about).pack(side=SL, padx=(14, 4))
        ttk.Button(header, text=T("⚙ الإعدادات"), style="Header.TButton", command=self.settings_dialog).pack(side=SL, padx=4)
        ttk.Button(header, text=T("🖼 الصور المتشابهة"), style="Header.TButton", command=self.similar_dialog).pack(side=SL, padx=4)
        ttk.Button(header, text=T("👁 المعاينة"), style="Header.TButton", command=self.toggle_preview).pack(side=SL, padx=4)

        # شريط المجلد
        top = ttk.Frame(self, padding=(10, 8))
        top.pack(fill="x")
        ttk.Label(top, text=T("المجلد:")).pack(side=SR)
        ttk.Button(top, text=T("📁 اختيار مجلد"), command=self.choose_folder).pack(side=SR, padx=4)
        self.folder_cb = ttk.Combobox(top, textvariable=self.root_dir, values=S["recent"], justify="left")
        self.folder_cb.pack(side=SR, fill="x", expand=True, padx=4)
        self.folder_cb.bind("<<ComboboxSelected>>", lambda e: self.start_scan())
        self.folder_cb.bind("<Return>", lambda e: self.start_scan())
        ttk.Label(top, text=T("📌 بدون المجلدات الفرعية"), style="Muted.TLabel").pack(side=SR, padx=8)
        ttk.Button(top, text=T("🔍 فحص"), style="Accent.TButton", command=self.start_scan).pack(side=SR, padx=4)

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10)
        self.preview_panel = None
        if S["show_preview"]:
            self.preview_panel = ttk.Frame(body, style="Panel.TFrame", padding=10)
            body.add(self.preview_panel, weight=1)
            self._build_preview(self.preview_panel)
        files_panel = ttk.Frame(body)
        types_panel = ttk.Frame(body)
        body.add(files_panel, weight=3)
        body.add(types_panel, weight=1)

        def init_sashes():
            w = body.winfo_width()
            if w < 50:
                return self.after(50, init_sashes)
            if self.preview_panel is not None:
                body.sashpos(0, 310)
                body.sashpos(1, w - 360)
            else:
                body.sashpos(0, w - 360)
        self.after(80, init_sashes)

        # ملخص الأنواع
        ttk.Label(types_panel, text=T("الأنواع واللواحق"), style="Title.TLabel").pack(anchor=AE, pady=(0, 4), padx=4)
        self.summary = ttk.Treeview(types_panel, columns=("count", "size", "pct"), selectmode="browse")
        for col, t, w in (("#0", T("النوع / اللاحقة"), 150), ("count", T("العدد"), 60),
                          ("size", T("الحجم"), 85), ("pct", T("النسبة"), 60)):
            self.summary.heading(col, text=t)
            self.summary.column(col, width=w, anchor=AE if col == "#0" else "center")
        sb = ttk.Scrollbar(types_panel, command=self.summary.yview)
        self.summary.configure(yscrollcommand=sb.set)
        sb.pack(side=SL, fill="y")
        self.summary.pack(fill="both", expand=True, padx=(0, 4))
        self.summary.bind("<<TreeviewSelect>>", self.on_summary_select)
        self.summary.tag_configure("cat", foreground=ACCENT)

        # الفلترة
        fbar = ttk.Frame(files_panel)
        fbar.pack(fill="x", pady=(0, 4))
        ttk.Label(fbar, text=T("بحث:")).pack(side=SR)
        ttk.Entry(fbar, textvariable=self.search, width=16).pack(side=SR, padx=4)
        ttk.Label(fbar, text=T("الحجم:")).pack(side=SR, padx=(10, 0))
        cb = ttk.Combobox(fbar, textvariable=self.size_filter, state="readonly",
                          values=[s[0] for s in SIZE_FILTERS], justify=JR, width=15)
        cb.pack(side=SR, padx=4)
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_files())
        ttk.Label(fbar, text=T("التاريخ:")).pack(side=SR, padx=(10, 0))
        cbd = ttk.Combobox(fbar, textvariable=self.date_filter, state="readonly", width=13,
                           values=[d[0] for d in DATE_FILTERS], justify=JR)
        cbd.pack(side=SR, padx=4)
        cbd.bind("<<ComboboxSelected>>", lambda e: self.refresh_files())
        self.search_entry = fbar.winfo_children()[1]
        self.filter_lbl = ttk.Label(fbar, text="", foreground=ACCENT)
        self.filter_lbl.pack(side=SL)

        # جدول الملفات
        cols = ("name", "ext", "size", "date", "folder")
        self.table = ttk.Treeview(files_panel, columns=cols, show="headings", selectmode="extended")
        heads = {"name": (T("اسم الملف"), 280), "ext": (T("اللاحقة"), 75), "size": (T("الحجم"), 90),
                 "date": (T("آخر تعديل"), 140), "folder": (T("التصنيف"), 140)}
        for c in cols:
            t, w = heads[c]
            self.table.heading(c, text=t, command=lambda c=c: self.sort_by(c))
            self.table.column(c, width=w, anchor="w" if c == "name" else "center")
        ys = ttk.Scrollbar(files_panel, command=self.table.yview)
        self.table.configure(yscrollcommand=ys.set)
        ys.pack(side=SR, fill="y")
        self.table.pack(fill="both", expand=True)
        self.table.tag_configure("odd", background=ODD)
        self.table.bind("<Double-1>", lambda e: self.open_selected())
        self.table.bind("<Button-3>", self.popup_menu)
        self.table.bind("<Button-2>", self.popup_menu)
        self.table.bind("<<TreeviewSelect>>", self.on_table_select)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label=T("فتح الملف"), command=self.open_selected)
        self.menu.add_command(label=T("فتح مكان الملف"), command=self.reveal_selected)
        self.menu.add_separator()
        self.menu.add_command(label=T("نقل المحدد إلى..."), command=self.move_selected)
        self.menu.add_command(label=T("نقل كل المعروض إلى..."), command=self.move_filtered)
        self.menu.add_command(label=T("إعادة تسمية..."), command=self.rename_dialog)
        self.menu.add_command(label=T("نسخ المسار"), command=self.copy_path)
        self.menu.add_separator()
        self.menu.add_command(label=T("🗑 لسلة المحذوفات"), command=self.trash_selected)

        for seq, fn in (("<Control-a>", self.select_all), ("<Control-A>", self.select_all),
                        ("<Delete>", self.trash_selected), ("<F2>", self.rename_dialog),
                        ("<Return>", self.open_selected)):
            self.table.bind(seq, lambda e, fn=fn: (fn(), "break")[1])
        self.bind("<F5>", lambda e: self.start_scan())
        self.bind("<Control-z>", lambda e: self.do_undo())
        self.bind("<Control-Z>", lambda e: self.do_undo())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind("<Control-F>", lambda e: self.search_entry.focus_set())

        # الأزرار
        bottom = ttk.Frame(self, padding=(10, 8))
        bottom.pack(fill="x")
        ttk.Button(bottom, text=T("✨ تنظيم تلقائي..."), style="Accent.TButton",
                   command=self.organize_dialog).pack(side=SR, padx=3)
        ttk.Button(bottom, text=T("🖼 الصور المتشابهة"), style="Accent.TButton",
                   command=self.similar_dialog).pack(side=SR, padx=3)
        ttk.Button(bottom, text=T("📑 الملفات المكررة"), style="Accent.TButton",
                   command=self.duplicates_dialog).pack(side=SR, padx=3)
        ttk.Button(bottom, text=T("✏ إعادة تسمية (F2)"), command=self.rename_dialog).pack(side=SR, padx=3)
        ttk.Button(bottom, text=T("📦 نقل المحدد..."), command=self.move_selected).pack(side=SR, padx=3)
        ttk.Button(bottom, text=T("🗑 حذف (Del)"), command=self.trash_selected).pack(side=SR, padx=3)
        self.undo_btn = ttk.Button(bottom, text=T("↩ تراجع (Ctrl+Z)"), command=self.do_undo)
        self.undo_btn.pack(side=SL, padx=3)


        sbar = ttk.Frame(self, style="Header.TFrame")
        sbar.pack(fill="x", side="bottom")
        ttk.Label(sbar, textvariable=self.status, style="Status.TLabel", anchor=AE).pack(side=SR, fill="x", expand=True)
        ttk.Label(sbar, text=f"© {DEV_NAME}  •  v{APP_VERSION}", style="Status.TLabel").pack(side=SL)

    # ---------- إعادة بناء الواجهة (بعد تغيير الثيم أو الخط)
    def rebuild_ui(self):
        for w in self.winfo_children():
            w.destroy()
        apply_theme(self)
        self._build()
        self._update_undo_btn()
        if self.files:
            self.build_summary()
            self.refresh_files()

    def toggle_preview(self):
        S["show_preview"] = not S["show_preview"]
        S.save()
        self.rebuild_ui()

    def on_table_select(self, _e=None):
        self.update_status()
        sel = self.selected_files()
        if self.preview_panel is not None:
            self.show_preview(sel[0] if len(sel) == 1 else None, len(sel))

    # ---------- المعاينة
    def _build_preview(self, p):
        ttk.Label(p, text=T("المعاينة"), style="Title.TLabel", background=PANEL).pack(anchor=AE)
        self.pv_name = ttk.Label(p, text=T("اختار ملف لتشوف معاينته"), style="Panel.TLabel",
                                 font=F(11, True), wraplength=300, justify=JR)
        self.pv_name.pack(anchor=AE, pady=(6, 8), fill="x")
        self.pv_box = tk.Frame(p, bg=FIELD, height=260, highlightthickness=1, highlightbackground=LINE)
        self.pv_box.pack(fill="x")
        self.pv_box.pack_propagate(False)
        self.pv_img = tk.Label(self.pv_box, bg=FIELD, fg=MUTED, font=F(40))
        self.pv_text = tk.Text(self.pv_box, bg=FIELD, fg=FG, relief="flat", wrap="none",
                               font=("Consolas", 9), insertbackground=FG, padx=6, pady=6)
        self.pv_img.pack(fill="both", expand=True)
        self.pv_info = ttk.Frame(p, style="Panel.TFrame")
        self.pv_info.pack(fill="x", pady=(10, 6))
        btns = ttk.Frame(p, style="Panel.TFrame")
        btns.pack(fill="x", pady=(4, 0))
        self.pv_open = ttk.Button(btns, text=T("▶ فتح الملف"), command=self.open_selected)
        self.pv_open.pack(side=SR, padx=2)
        self.pv_reveal = ttk.Button(btns, text=T("📂 مكانه"), command=self.reveal_selected)
        self.pv_reveal.pack(side=SR, padx=2)
        self.show_preview(None)

    def _pv_mode(self, mode):
        self.pv_img.pack_forget()
        self.pv_text.pack_forget()
        (self.pv_text if mode == "text" else self.pv_img).pack(fill="both", expand=True)

    def show_preview(self, f, count=0):
        for w in self.pv_info.winfo_children():
            w.destroy()
        self.preview_img = None
        self._pv_mode("img")
        self.pv_img.config(image="", text="")
        if f is None:
            self.pv_name.config(text=T("تم تحديد {0} ملف").format(count) if count > 1 else T("اختار ملف لتشوف معاينته"))
            self.pv_img.config(text="🗂" if count > 1 else "👁")
            for b in (self.pv_open, self.pv_reveal):
                b.state(["disabled"])
            if count > 1:
                total = sum(x["size"] for x in self.selected_files())
                self._info_row(T("الحجم الكلي"), human(total))
            return
        for b in (self.pv_open, self.pv_reveal):
            b.state(["!disabled"])
        self.pv_name.config(text=f["name"])
        ext = f["ext"].lower()
        extra = None
        shown = False
        if f["cat"] == T("صور") or ext in IMAGE_EXTS:
            self.pv_box.update_idletasks()
            bw = max(160, self.pv_box.winfo_width() - 12)
            img, extra = load_thumb(f["path"], bw, 246)
            if img:
                self.preview_img = img
                self.pv_img.config(image=img)
                shown = True
        elif ext in TEXT_EXTS and f["size"] < 5 * MB:
            try:
                with open(f["path"], "rb") as fh:
                    data = fh.read(30000)
                txt = data.decode("utf-8", errors="replace")
                self._pv_mode("text")
                self.pv_text.config(state="normal")
                self.pv_text.delete("1.0", "end")
                self.pv_text.insert("1.0", txt)
                self.pv_text.config(state="disabled")
                shown = True
            except OSError:
                pass
        if not shown:
            self.pv_img.config(text=ICONS.get(f["cat"], "📄"))
        self._info_row(T("النوع"), f"{f['cat']}  •  {f['ext']}")
        self._info_row(T("الحجم"), T("{0}  ({1:,} بايت)").format(human(f['size']), f['size']))
        if extra:
            self._info_row(T("الأبعاد"), extra)
        self._info_row(T("آخر تعديل"), datetime.fromtimestamp(f["mtime"]).strftime("%Y-%m-%d  %H:%M"))
        try:
            self._info_row(T("تاريخ الإنشاء"), datetime.fromtimestamp(os.path.getctime(f["path"])).strftime("%Y-%m-%d  %H:%M"))
        except OSError:
            pass
        self._info_row(T("المكان"), os.path.dirname(f["path"]))

    def _info_row(self, k, v):
        r = ttk.Frame(self.pv_info, style="Panel.TFrame")
        r.pack(fill="x", pady=2)
        ttk.Label(r, text=k, style="PanelMuted.TLabel", width=13, anchor=AE).pack(side=SR)
        ttk.Label(r, text=v, style="Panel.TLabel", wraplength=220, justify=JR, anchor=AE).pack(side=SR, fill="x", expand=True)

    # ---------- الفحص
    def choose_folder(self):
        d = filedialog.askdirectory(title=T("اختر المجلد"), initialdir=self.root_dir.get() or None)
        if d:
            self.root_dir.set(os.path.normpath(d))
            self.start_scan()

    def start_scan(self):
        root = self.root_dir.get().strip()
        if not root or not os.path.isdir(root):
            messagebox.showwarning(APP_TITLE, T("اختر مجلداً صحيحاً أولاً."))
            return
        S["last_folder"] = root
        S["recent"] = [root] + [r for r in S["recent"] if os.path.normcase(r) != os.path.normcase(root)][:9]
        try:
            self.folder_cb.configure(values=S["recent"])
        except tk.TclError:
            pass
        self.status.set(T("جارٍ الفحص..."))
        self.config(cursor="watch")

        def prog(n):
            self.after(0, lambda: self.status.set(T("جارٍ الفحص... {0} ملف").format(n)))

        def work():
            files = scan_folder(root, False, prog)  # المجلد المحدد فقط، بدون المجلدات الفرعية
            self.after(0, lambda: self.scan_done(files))

        threading.Thread(target=work, daemon=True).start()

    def scan_done(self, files):
        self.config(cursor="")
        self.files = files
        self.sel_cat = self.sel_ext = None
        self.build_summary()
        self.refresh_files()

    def build_summary(self):
        self.summary.delete(*self.summary.get_children())
        total_size = sum(f["size"] for f in self.files)
        total = total_size or 1
        cats = {}
        for f in self.files:
            c = cats.setdefault(f["cat"], {"n": 0, "s": 0, "ext": {}})
            c["n"] += 1
            c["s"] += f["size"]
            e = c["ext"].setdefault(f["ext"], [0, 0])
            e[0] += 1
            e[1] += f["size"]
        self.summary.insert("", "end", iid="all", text=T("📁 الكل"), tags=("cat",),
                            values=(len(self.files), human(total_size), "100%"))
        for cat, c in sorted(cats.items(), key=lambda kv: -kv[1]["s"]):
            cid = f"cat::{cat}"
            self.summary.insert("", "end", iid=cid, text=f"{ICONS.get(cat, '📁')} {cat}", tags=("cat",),
                                values=(c["n"], human(c["s"]), f"{100 * c['s'] / total:.1f}%"))
            for ext, (n, s) in sorted(c["ext"].items(), key=lambda kv: -kv[1][1]):
                self.summary.insert(cid, "end", iid=f"ext::{cat}::{ext}", text=ext,
                                    values=(n, human(s), f"{100 * s / total:.1f}%"))

    def on_summary_select(self, _e=None):
        sel = self.summary.selection()
        if not sel:
            return
        parts = sel[0].split("::")
        self.sel_cat = parts[1] if len(parts) > 1 else None
        self.sel_ext = parts[2] if len(parts) > 2 else None
        self.refresh_files()

    # ---------- العرض والفلترة
    def refresh_files(self):
        q = self.search.get().strip().lower()
        lo, hi = next((a, b) for n, a, b in SIZE_FILTERS if n == self.size_filter.get())
        days = dict(DATE_FILTERS).get(self.date_filter.get())
        now = datetime.now().timestamp()
        if days is None:
            dmin, dmax = 0, float("inf")
        elif days > 0:
            dmin, dmax = now - days * 86400, float("inf")
        else:
            dmin, dmax = 0, now + days * 86400
        res = [f for f in self.files
               if (not self.sel_cat or f["cat"] == self.sel_cat)
               and (not self.sel_ext or f["ext"] == self.sel_ext)
               and f["size"] >= lo and (hi is None or f["size"] < hi)
               and dmin <= f["mtime"] <= dmax
               and (not q or q in f["name"].lower())]
        key = {"name": lambda f: f["name"].lower(), "ext": lambda f: f["ext"],
               "size": lambda f: f["size"], "date": lambda f: f["mtime"],
               "folder": lambda f: f["cat"]}[self.sort_key]
        res.sort(key=key, reverse=self.sort_desc)
        self.filtered = res

        self.table.delete(*self.table.get_children())
        root = self.root_dir.get()
        for i, f in enumerate(res[:int(S["max_rows"])]):
            rel = f"{ICONS.get(f['cat'], '📁')} {f['cat']}"
            self.table.insert("", "end", iid=str(i), tags=("odd",) if i % 2 else (), values=(
                f["name"], f["ext"], human(f["size"]),
                datetime.fromtimestamp(f["mtime"]).strftime("%Y-%m-%d %H:%M"), rel))

        label = T("الكل") if not self.sel_cat else self.sel_cat + (f" ← {self.sel_ext}" if self.sel_ext else "")
        self.filter_lbl.config(text=T("المعروض: {0}").format(label))
        for c in ("name", "ext", "size", "date", "folder"):
            t = self.table.heading(c, "text").rstrip(" ▲▼")
            self.table.heading(c, text=t + ((" ▼" if self.sort_desc else " ▲") if c == self.sort_key else ""))
        self.update_status()

    def sort_by(self, col):
        if self.sort_key == col:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_key, self.sort_desc = col, col in ("size", "date")
        self.refresh_files()

    def update_status(self):
        n, s = len(self.filtered), sum(f["size"] for f in self.filtered)
        sel = self.selected_files()
        txt = T("المعروض: {0} ملف ({1})").format(n, human(s))
        if n > int(S["max_rows"]):
            txt += T("  —  الجدول يعرض أول {0} فقط، لكن «نقل كل المعروض» يشمل الكل").format(S['max_rows'])
        if sel:
            txt += T("   |   المحدد: {0} ملف ({1})").format(len(sel), human(sum(f['size'] for f in sel)))
        self.status.set(txt)

    def selected_files(self):
        return [self.filtered[int(i)] for i in self.table.selection()]

    # ---------- إجراءات
    def popup_menu(self, e):
        row = self.table.identify_row(e.y)
        if row and row not in self.table.selection():
            self.table.selection_set(row)
        if row:
            self.menu.tk_popup(e.x_root, e.y_root)

    def open_selected(self):
        sel = self.selected_files()
        if sel:
            open_path(sel[0]["path"])

    def reveal_selected(self):
        sel = self.selected_files()
        if sel:
            reveal_path(sel[0]["path"])

    def _move_to_folder(self, files):
        if not files:
            messagebox.showinfo(APP_TITLE, T("ما في ملفات محددة."))
            return
        dest = filedialog.askdirectory(title=T("اختر المجلد الذي سيتم النقل إليه"),
                                       initialdir=self.root_dir.get() or None)
        if not dest:
            return
        dest = os.path.normpath(dest)
        if S["confirm"] and not messagebox.askyesno(
                APP_TITLE, T("نقل {0} ملف ({1})\nإلى:\n{2} ؟").format(len(files), human(sum(f['size'] for f in files)), dest)):
            return
        plan = [(f["path"], dest) for f in files
                if os.path.normcase(os.path.dirname(f["path"])) != os.path.normcase(dest)]
        self.run_plan(plan)

    def move_selected(self):
        self._move_to_folder(self.selected_files())

    def move_filtered(self):
        self._move_to_folder(self.filtered)

    def run_plan(self, plan):
        if not plan:
            messagebox.showinfo(APP_TITLE, T("كل الملفات بمكانها الصحيح، ما في شي ينقل."))
            return
        moved, created, errors = execute_moves(plan)
        if moved:
            save_undo(moved, created, T("نقل"))
        msg = T("تم نقل {0} ملف ✅").format(len(moved))
        if errors:
            msg += T("\n\nفشل نقل {0} ملف:\n").format(len(errors)) + "\n".join(errors[:10])
        messagebox.showinfo(APP_TITLE, msg)
        self._update_undo_btn()
        self.start_scan()

    def do_undo(self):
        data = load_undo()
        if not data:
            messagebox.showinfo(APP_TITLE, T("لا توجد عملية للتراجع عنها."))
            return
        if not messagebox.askyesno(APP_TITLE, T("التراجع عن آخر عملية «{0}»؟\n{1} ملف بيرجعوا متل ما كانوا.\n(العملية من: {2})").format(data.get('label', 'نقل'), len(data['moved']), data['time'].replace('T', '  '))):
            return
        ok, errors = undo_last()
        msg = T("تم إرجاع {0} ملف ✅").format(ok)
        if errors:
            msg += "\n\n" + "\n".join(errors[:10])
        messagebox.showinfo(APP_TITLE, msg)
        self._update_undo_btn()
        if self.root_dir.get():
            self.start_scan()

    def _update_undo_btn(self):
        n = undo_count()
        self.undo_btn.state(["!disabled"] if n else ["disabled"])
        self.undo_btn.config(text=T("↩ تراجع (Ctrl+Z)").format() + (f"  [{n}]" if n else ""))

    def restart_app(self):
        S["recursive"] = self.recursive.get()
        S.save()
        env = os.environ.copy()
        env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        try:
            if getattr(sys, "frozen", False):
                subprocess.Popen([sys.executable], env=env)
            else:
                subprocess.Popen([sys.executable, os.path.abspath(sys.argv[0])], env=env)
        except Exception:  # noqa
            pass
        self.destroy()

    def on_close(self):
        S["recursive"] = self.recursive.get()
        S.save()
        self.destroy()

    # ---------- نافذة جانبية
    def _dialog(self, title, size):
        win = tk.Toplevel(self)
        win.title(f"{title}  —  {DEV_NAME}")
        win.geometry(size)
        win.configure(bg=BG)
        win.transient(self)
        win.grab_set()
        if self.img_icon:
            win.iconphoto(False, self.img_icon)
        return win

    # ---------- حول
    def about(self):
        win = self._dialog(T("حول"), "420x430")
        win.resizable(False, False)
        frm = ttk.Frame(win, padding=20)
        frm.pack(fill="both", expand=True)
        if self.img_avatar:
            ttk.Label(frm, image=self.img_avatar).pack(pady=(0, 10))
        if self.img_logo:
            ttk.Label(frm, image=self.img_logo).pack()
        ttk.Label(frm, text=T("{0}  •  الإصدار {1}").format(APP_NAME, APP_VERSION), font=F(12, True)).pack(pady=(10, 2))
        ttk.Label(frm, text=T("تطوير وتصميم: {0}").format(DEV_NAME), style="Muted.TLabel").pack()
        link = ttk.Label(frm, text=DEV_LINK.replace("https://", ""), foreground=ACCENT, cursor="hand2",
                         font=F(10, extra="underline"))
        link.pack(pady=(6, 12))
        link.bind("<Button-1>", lambda e: webbrowser.open(DEV_LINK))
        ttk.Button(frm, text=T("إغلاق"), command=win.destroy).pack()

    # ---------- الإعدادات
    def settings_dialog(self):
        win = self._dialog(T("الإعدادات"), "720x680")
        cats = dict(S["categories"])

        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        # --- تبويب الأنواع
        t1 = ttk.Frame(nb, padding=10)
        nb.add(t1, text=T("الأنواع واللواحق"))
        ttk.Label(t1, text=T("اختار نوع من القائمة وعدّل لواحقه (افصل بينها بمسافة). الملفات اللي لاحقتها مو موجودة بتروح لـ «أخرى»."),
                  style="Muted.TLabel", wraplength=620, justify=JR).pack(anchor=AE, pady=(0, 8))
        row = ttk.Frame(t1)
        row.pack(fill="both", expand=True)
        lb = dark_listbox(row, width=18, justify=JR, exportselection=False)
        lb.pack(side=SR, fill="y")
        edit = ttk.Frame(row, padding=(0, 0, 10, 0))
        edit.pack(side=SR, fill="both", expand=True)

        name_var = tk.StringVar()
        ttk.Label(edit, text=T("اسم النوع (هو اسم المجلد وقت التنظيم):")).pack(anchor=AE)
        ttk.Entry(edit, textvariable=name_var, justify=JR).pack(fill="x", pady=(2, 8))
        ttk.Label(edit, text=T("اللواحق:")).pack(anchor=AE)
        ext_txt = tk.Text(edit, height=8, bg=FIELD, fg=FG, insertbackground=FG, relief="flat",
                          highlightthickness=1, highlightbackground=LINE, highlightcolor=ACCENT, wrap="word")
        ext_txt.pack(fill="both", expand=True, pady=(2, 8))
        state = {"cur": None}

        def fill_list(select=None):
            lb.delete(0, "end")
            for c in cats:
                lb.insert("end", f"{ICONS.get(c, '📁')} {c}")
            names = list(cats)
            if names:
                i = names.index(select) if select in names else 0
                lb.selection_set(i)
                show(names[i])

        def store():
            cur = state["cur"]
            if cur is None or cur not in cats:
                return cur
            new = name_var.get().strip() or cur
            exts = " ".join(e.lower().lstrip(".") for e in ext_txt.get("1.0", "end").replace(",", " ").split())
            if new != cur:
                items = [(new if k == cur else k, v) for k, v in cats.items()]
                cats.clear()
                cats.update(items)
            cats[new] = exts
            state["cur"] = new
            return new

        def show(name):
            state["cur"] = name
            name_var.set(name)
            ext_txt.delete("1.0", "end")
            ext_txt.insert("1.0", cats[name])

        def on_pick(_e=None):
            sel = lb.curselection()
            if not sel:
                return
            target = list(cats)[sel[0]]
            store()
            fill_list(select=target if target in cats else None)

        lb.bind("<<ListboxSelect>>", on_pick)

        def add_cat():
            store()
            n, i = T("نوع جديد"), 1
            while n in cats:
                i += 1
                n = T("نوع جديد {0}").format(i)
            cats[n] = ""
            fill_list(select=n)

        def del_cat():
            cur = state["cur"]
            if cur and messagebox.askyesno(APP_TITLE, T("حذف النوع «{0}»؟").format(cur), parent=win):
                cats.pop(cur, None)
                state["cur"] = None
                fill_list()

        def reset_cats():
            if messagebox.askyesno(APP_TITLE, T("إرجاع الأنواع للوضع الافتراضي؟"), parent=win):
                cats.clear()
                cats.update(DEFAULT_CATEGORIES)
                state["cur"] = None
                fill_list()

        b = ttk.Frame(edit)
        b.pack(fill="x")
        ttk.Button(b, text=T("➕ نوع جديد"), command=add_cat).pack(side=SR, padx=2)
        ttk.Button(b, text=T("🗑 حذف النوع"), command=del_cat).pack(side=SR, padx=2)
        ttk.Button(b, text=T("↺ الافتراضي"), command=reset_cats).pack(side=SL, padx=2)

        # --- تبويب عام
        t2 = ttk.Frame(nb, padding=14)
        nb.add(t2, text=T("خيارات عامة"))
        v_rec = tk.BooleanVar(value=self.recursive.get())
        v_hidden = tk.BooleanVar(value=S["skip_hidden"])
        v_confirm = tk.BooleanVar(value=S["confirm"])
        v_rows = tk.IntVar(value=int(S["max_rows"]))
        v_other = tk.StringVar(value=S["other_name"])
        v_mode = tk.StringVar(value=S["default_mode"])

        ttk.Checkbutton(t2, text=T("تجاهل الملفات والمجلدات المخفية"), variable=v_hidden).pack(anchor=AE, pady=3)
        ttk.Checkbutton(t2, text=T("اسألني للتأكيد قبل النقل"), variable=v_confirm).pack(anchor=AE, pady=3)
        r = ttk.Frame(t2)
        r.pack(anchor=AE, pady=8)
        ttk.Label(r, text=T("أقصى عدد ملفات يُعرض بالجدول:")).pack(side=SR)
        ttk.Spinbox(r, from_=500, to=100000, increment=500, textvariable=v_rows, width=8).pack(side=SR, padx=6)
        r2 = ttk.Frame(t2)
        r2.pack(anchor=AE, pady=4)
        ttk.Label(r2, text=T("اسم مجلد الملفات غير المصنفة:")).pack(side=SR)
        ttk.Entry(r2, textvariable=v_other, width=14, justify=JR).pack(side=SR, padx=6)
        ttk.Label(t2, text=T("طريقة التنظيم الافتراضية:"), style="Title.TLabel").pack(anchor=AE, pady=(12, 4))
        for val, txt in ORGANIZE_MODES:
            ttk.Radiobutton(t2, text=txt, value=val, variable=v_mode).pack(anchor=AE, padx=10)

        # --- تبويب المظهر
        t3 = ttk.Frame(nb, padding=14)
        nb.add(t3, text=T("المظهر والخط"))
        v_theme = tk.StringVar(value=S["theme"])
        v_font = tk.StringVar(value=S["font"])
        v_prev = tk.BooleanVar(value=S["show_preview"])
        ttk.Label(t3, text=T("الألوان:"), style="Title.TLabel").pack(anchor=AE)
        grid = ttk.Frame(t3)
        grid.pack(anchor=AE, pady=(4, 12))
        for i, (name, vals) in enumerate(THEMES.items()):
            th = dict(zip(_K, vals))
            cell = ttk.Frame(grid, padding=4)
            cell.grid(row=i // 3, column=(2 - i % 3) if RTL else i % 3, padx=4, pady=4, sticky=AE)
            sw = tk.Frame(cell, bg=th["BG"], width=120, height=34, highlightthickness=2,
                          highlightbackground=th["LINE"])
            sw.pack()
            sw.pack_propagate(False)
            tk.Frame(sw, bg=th["ACCENT"], width=30).pack(side=SR, fill="y")
            tk.Frame(sw, bg=th["PANEL"], width=40).pack(side=SR, fill="y")
            ttk.Radiobutton(cell, text=T(name), value=name, variable=v_theme).pack(anchor=AE)
        ttk.Label(t3, text=T("الخط:"), style="Title.TLabel").pack(anchor=AE)
        from tkinter import font as tkfont
        fams = sorted(f for f in set(tkfont.families(self)) if not f.startswith("@"))
        fr = ttk.Frame(t3)
        fr.pack(anchor=AE, fill="x", pady=4)
        ttk.Combobox(fr, textvariable=v_font, values=[PREFERRED_FONT] + fams, width=28).pack(side=SR)
        sample = ttk.Label(t3, text="", style="Muted.TLabel", wraplength=640, justify=JR)
        sample.pack(anchor=AE, pady=4)

        def upd_sample(*_):
            fam = v_font.get()
            ok = any(x == fam or x.startswith(fam + " ") for x in fams)
            sample.config(font=(fam, 12) if ok else F(12),
                          text=T("نموذج: منظّم الملفات من GraphicWO  123") if ok else
                          T("الخط «{0}» مو منزّل على الجهاز — رح يستخدم {1} لحد ما تنزّله أو تحطّه بمجلد fonts").format(fam, FONT['regular']))
        v_font.trace_add("write", upd_sample)
        upd_sample()
        ttk.Checkbutton(t3, text=T("إظهار لوحة المعاينة"), variable=v_prev).pack(anchor=AE, pady=(12, 0))
        LANG_NAMES = {"ar": "العربية", "en": "English", "fr": "Français"}
        lr = ttk.Frame(t3)
        lr.pack(anchor=AE, pady=(14, 0))
        ttk.Label(lr, text=T("اللغة:"), style="Title.TLabel").pack(side=SR)
        v_lang = tk.StringVar(value=LANG_NAMES[LANG])
        ttk.Combobox(lr, textvariable=v_lang, state="readonly", width=12,
                     values=list(LANG_NAMES.values())).pack(side=SR, padx=8)

        # --- حفظ
        btns = ttk.Frame(win, padding=(10, 0, 10, 10))
        btns.pack(fill="x")

        def save():
            store()
            S["categories"] = {k: v for k, v in cats.items() if k.strip()}
            S["skip_hidden"] = v_hidden.get()
            S["confirm"] = v_confirm.get()
            try:
                S["max_rows"] = max(100, int(v_rows.get()))
            except (tk.TclError, ValueError):
                pass
            S["other_name"] = v_other.get().strip() or T("أخرى")
            S["default_mode"] = v_mode.get()
            S["recursive"] = v_rec.get()
            self.recursive.set(v_rec.get())
            look = (S["theme"], S["font"], S["show_preview"])
            S["theme"] = v_theme.get()
            S["font"] = v_font.get().strip() or PREFERRED_FONT
            S["show_preview"] = v_prev.get()
            new_lang = {v: k for k, v in LANG_NAMES.items()}.get(v_lang.get(), LANG)
            S["lang"] = new_lang
            S.save()
            win.destroy()
            if new_lang != LANG:
                messagebox.showinfo(APP_TITLE, T("رح يعيد البرنامج التشغيل لتتغيّر اللغة."))
                self.restart_app()
                return
            if look != (S["theme"], S["font"], S["show_preview"]):
                self.rebuild_ui()
            if self.files and os.path.isdir(self.root_dir.get()):
                self.start_scan()

        ttk.Button(btns, text=T("💾 حفظ"), style="Accent.TButton", command=save).pack(side=SR)
        ttk.Button(btns, text=T("إلغاء"), command=win.destroy).pack(side=SL)
        fill_list()

    # ---------- أدوات سريعة
    def select_all(self):
        self.table.selection_set(self.table.get_children())

    def copy_path(self):
        sel = self.selected_files()
        if sel:
            self.clipboard_clear()
            self.clipboard_append("\n".join(f["path"] for f in sel))
            self.status.set(T("تم نسخ مسار {0} ملف 📋").format(len(sel)))

    def trash_selected(self, files=None, parent=None):
        files = files if files is not None else self.selected_files()
        if not files:
            messagebox.showinfo(APP_TITLE, T("حدد الملفات اللي بدك تحذفها."), parent=parent or self)
            return False
        if not messagebox.askyesno(APP_TITLE, T("نقل {0} ملف ({1}) لسلة المحذوفات؟\nفيك ترجعهن من سلة المحذوفات بالويندوز.").format(len(files), human(sum(f['size'] for f in files))),
                                   icon="warning", parent=parent or self):
            return False
        ok, errors = send_to_trash([f["path"] for f in files])
        msg = T("انحذف {0} ملف لسلة المحذوفات 🗑").format(ok)
        if errors:
            msg += T("\n\nما انحذفوا ({0}):\n").format(len(errors)) + "\n".join(errors[:10])
        messagebox.showinfo(APP_TITLE, msg, parent=parent or self)
        self.start_scan()
        return True

    # ---------- إعادة التسمية الجماعية
    def rename_dialog(self):
        files = self.selected_files() or list(self.filtered)
        if not files:
            messagebox.showwarning(APP_TITLE, T("افحص مجلداً أولاً."))
            return
        src_label = T("المحددة") if self.selected_files() else T("المعروضة")
        win = self._dialog(T("إعادة تسمية جماعية"), "900x640")
        pattern = tk.StringVar(value="{name}")
        find = tk.StringVar()
        replace = tk.StringVar()
        start = tk.IntVar(value=1)
        digits = tk.IntVar(value=3)
        case = tk.StringVar(value="keep")
        lower_ext = tk.BooleanVar(value=False)
        order = tk.StringVar(value=T("الترتيب الحالي"))

        frm = ttk.Frame(win, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=T("إعادة تسمية {0} ملف ({1})").format(len(files), src_label), style="Title.TLabel").pack(anchor=AE)
        r1 = ttk.Frame(frm)
        r1.pack(fill="x", pady=(8, 2))
        ttk.Label(r1, text=T("شكل الاسم الجديد:")).pack(side=SR)
        ent = ttk.Entry(r1, textvariable=pattern, justify="left", font=F(11))
        ent.pack(side=SR, fill="x", expand=True, padx=6)
        r1b = ttk.Frame(frm)
        r1b.pack(fill="x")
        ttk.Label(r1b, text=T("ضيف:"), style="Muted.TLabel").pack(side=SR)
        presets = [(T("الاسم"), "{name}"), (T("رقم"), "{n}"), (T("تاريخ التصوير/التعديل"), "{date}"),
                   (T("الوقت"), "{time}"), (T("النوع"), "{cat}"), (T("اللاحقة"), "{ext}")]
        for t, tok in presets:
            ttk.Button(r1b, text=t, command=lambda tok=tok: ent.insert("insert", tok)).pack(side=SR, padx=2)
        r1c = ttk.Frame(frm)
        r1c.pack(fill="x", pady=(4, 0))
        ttk.Label(r1c, text=T("قوالب جاهزة:"), style="Muted.TLabel").pack(side=SR)
        for t, p in ((T("صور 2025-01-31 001"), "{date} {n}"), (T("الاسم_001"), "{name}_{n}"),
                     (T("رحلة 001"), T("رحلة {n}")), (T("رجوع للاسم"), "{name}")):
            ttk.Button(r1c, text=t, command=lambda p=p: pattern.set(p)).pack(side=SR, padx=2)

        r2 = ttk.Frame(frm)
        r2.pack(fill="x", pady=8)
        ttk.Label(r2, text=T("استبدال:")).pack(side=SR)
        ttk.Entry(r2, textvariable=find, width=14, justify=JR).pack(side=SR, padx=4)
        ttk.Label(r2, text=T("بـ")).pack(side=SR)
        ttk.Entry(r2, textvariable=replace, width=14, justify=JR).pack(side=SR, padx=4)
        ttk.Label(r2, text=T("   الرقم يبدأ من:")).pack(side=SR)
        ttk.Spinbox(r2, from_=0, to=99999, textvariable=start, width=6).pack(side=SR, padx=4)
        ttk.Label(r2, text=T("خانات:")).pack(side=SR)
        ttk.Spinbox(r2, from_=1, to=6, textvariable=digits, width=3).pack(side=SR, padx=4)

        r3 = ttk.Frame(frm)
        r3.pack(fill="x")
        ttk.Label(r3, text=T("الأحرف:")).pack(side=SR)
        for t, v in ((T("متل ما هي"), "keep"), (T("صغيرة"), "lower"), (T("كبيرة"), "upper"), (T("أول حرف كبير"), "title")):
            ttk.Radiobutton(r3, text=t, value=v, variable=case).pack(side=SR, padx=3)
        ttk.Checkbutton(r3, text=T("لاحقة صغيرة (.JPG ← .jpg)"), variable=lower_ext).pack(side=SR, padx=10)
        ttk.Label(r3, text=T("الترقيم حسب:")).pack(side=SR, padx=(10, 0))
        ttk.Combobox(r3, textvariable=order, state="readonly", width=14, justify=JR,
                     values=[T("الترتيب الحالي"), T("الاسم"), T("التاريخ (الأقدم أولاً)"), T("الحجم")]).pack(side=SR, padx=4)

        ttk.Label(frm, text=T("معاينة:"), style="Title.TLabel").pack(anchor=AE, pady=(10, 2))
        tv = ttk.Treeview(frm, columns=("old", "new"), show="headings", height=12)
        tv.heading("old", text=T("الاسم الحالي"))
        tv.heading("new", text=T("الاسم الجديد"))
        tv.column("old", width=400)
        tv.column("new", width=400)
        tv.tag_configure("same", foreground=MUTED)
        tv.tag_configure("bad", foreground="#ff6b6b")
        tv.pack(fill="both", expand=True)
        st = {"plan": []}

        def ordered():
            o = order.get()
            if o == T("الاسم"):
                return sorted(files, key=lambda f: f["name"].lower())
            if o.startswith(T("التاريخ")):
                return sorted(files, key=lambda f: f["mtime"])
            if o == T("الحجم"):
                return sorted(files, key=lambda f: -f["size"])
            return files

        def update(*_):
            try:
                opts = {"pattern": pattern.get(), "find": find.get(), "replace": replace.get(),
                        "start": int(start.get()), "digits": int(digits.get()), "case": case.get(),
                        "lower_ext": lower_ext.get()}
            except (tk.TclError, ValueError):
                return
            tv.delete(*tv.get_children())
            plan, seen = [], set()
            for i, f in enumerate(ordered()):
                new = build_new_name(f, i, opts) if ("{date}" not in opts["pattern"] and "{time}" not in opts["pattern"]) or i < 400 else f["name"]
                key = new.lower()
                tag = "same" if new == f["name"] else ("bad" if key in seen else "")
                seen.add(key)
                if new != f["name"]:
                    plan.append((f, new))
                if i < 400:
                    tv.insert("", "end", values=(f["name"], new), tags=(tag,) if tag else ())
            st["plan"] = plan
            go.config(text=T("✏ تسمية {0} ملف").format(len(plan)))

        for v in (pattern, find, replace, start, digits, case, lower_ext, order):
            v.trace_add("write", update)

        def run():
            if not st["plan"] and not any(t in pattern.get() for t in ("{date}", "{time}")):
                return
            if S["confirm"] and not messagebox.askyesno(APP_TITLE, T("إعادة تسمية {0} ملف؟\n(بتقدر تتراجع بعدين)").format(len(st['plan']) if len(files) <= 400 else len(files)), parent=win):
                return
            opts = {"pattern": pattern.get(), "find": find.get(), "replace": replace.get(),
                    "start": int(start.get()), "digits": int(digits.get()), "case": case.get(),
                    "lower_ext": lower_ext.get()}
            names = {f["path"]: build_new_name(f, i, opts) for i, f in enumerate(ordered())}
            plan = [(f, names[f["path"]]) for f in ordered() if names[f["path"]] != f["name"]]
            if not plan:
                win.destroy()
                return
            # مرحلتين لتفادي تضارب الأسماء
            moved, errors, temp = [], [], []
            for f, _ in plan:
                tmp = f["path"] + ".gwo_tmp"
                try:
                    os.rename(f["path"], tmp)
                    temp.append((f, tmp))
                except OSError as e:
                    errors.append(f"{f['name']}: {e}")
            for f, tmp in temp:
                d = os.path.dirname(f["path"])
                dst = os.path.join(d, names[f["path"]])
                if os.path.exists(dst):
                    dst = unique_path(d, names[f["path"]])
                try:
                    os.rename(tmp, dst)
                    moved.append((f["path"], dst))
                except OSError as e:
                    os.rename(tmp, f["path"])
                    errors.append(f"{f['name']}: {e}")
            if moved:
                save_undo(moved, [], T("إعادة تسمية"))
            win.destroy()
            msg = T("تمت إعادة تسمية {0} ملف ✅").format(len(moved))
            if errors:
                msg += "\n\n" + "\n".join(errors[:10])
            messagebox.showinfo(APP_TITLE, msg)
            self._update_undo_btn()
            self.start_scan()

        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(10, 0))
        go = ttk.Button(btns, text=T("تسمية"), style="Accent.TButton", command=run)
        go.pack(side=SR)
        ttk.Button(btns, text=T("إلغاء"), command=win.destroy).pack(side=SL)
        ttk.Label(btns, text=T("{date} بياخد تاريخ التصوير من الكاميرا للصور، وإلا تاريخ التعديل"),
                  style="Muted.TLabel").pack(side=SR, padx=12)
        update()
        ent.focus_set()

    # ---------- الملفات المكررة (تطابق تام)
    def duplicates_dialog(self):
        if not self.files:
            messagebox.showwarning(APP_TITLE, T("افحص مجلداً أولاً."))
            return
        win = self._dialog(T("الملفات المكررة"), "980x640")
        win.grab_release()
        info = tk.StringVar(value=T("جارٍ البحث عن الملفات المتطابقة..."))
        top = ttk.Frame(win, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text=T("ملفات متطابقة 100% (نفس المحتوى حتى لو الاسم مختلف)"), style="Title.TLabel").pack(side=SR)
        pb = ttk.Progressbar(top, length=220, mode="determinate")
        pb.pack(side=SL)
        ttk.Label(win, textvariable=info, style="Muted.TLabel", padding=(12, 0)).pack(anchor=AE)
        mid = ttk.Frame(win, padding=(10, 6))
        mid.pack(fill="both", expand=True)
        tv = ttk.Treeview(mid, columns=("size", "date", "keep"), selectmode="extended")
        tv.heading("#0", text=T("الملف"))
        tv.heading("size", text=T("الحجم"))
        tv.heading("date", text=T("آخر تعديل"))
        tv.heading("keep", text="")
        tv.column("#0", width=420)
        tv.column("size", width=100, anchor="center")
        tv.column("date", width=150, anchor="center")
        tv.column("keep", width=120, anchor="center")
        tv.tag_configure("grp", foreground=ACCENT)
        tv.tag_configure("keep", foreground=MUTED)
        sb = ttk.Scrollbar(mid, command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        sb.pack(side=SR, fill="y")
        tv.pack(fill="both", expand=True)
        st = {"groups": [], "map": {}}
        tv.bind("<Double-1>", lambda e: [open_path(st["map"][i]["path"]) for i in tv.selection()[:1] if i in st["map"]])

        def sel_files():
            return [st["map"][i] for i in tv.selection() if i in st["map"]]

        def render():
            tv.delete(*tv.get_children())
            st["map"].clear()
            waste = 0
            for gi, g in enumerate(st["groups"]):
                waste += g[0]["size"] * (len(g) - 1)
                gid = tv.insert("", "end", text=T("مجموعة {0} — {1} نسخ  ({2} للنسخة)").format(gi + 1, len(g), human(g[0]['size'])),
                                open=True, tags=("grp",))
                for k, f in enumerate(g):
                    iid = tv.insert(gid, "end", text=f["name"], values=(
                        human(f["size"]), datetime.fromtimestamp(f["mtime"]).strftime("%Y-%m-%d %H:%M"),
                        T("⭐ الأصلية (الأقدم)") if k == 0 else T("نسخة")), tags=("keep",) if k == 0 else ())
                    st["map"][iid] = f
            if not st["groups"]:
                info.set(T("ما في ملفات مكررة بهالمجلد 👌"))
            else:
                info.set(T("{0} مجموعة  •  {1} نسخة زايدة  •  بتوفّر {2}").format(len(st['groups']), sum(len(g) - 1 for g in st['groups']), human(waste)))

        def auto_select():
            tv.selection_set([iid for iid, f in st["map"].items()
                              if tv.index(iid) > 0])

        def move_sel():
            fs = sel_files()
            if not fs:
                messagebox.showinfo(APP_TITLE, T("حدد النسخ أولاً (أو اكبس «حدد النسخ الزايدة»)."), parent=win)
                return
            dest = os.path.join(self.root_dir.get(), T("ملفات مكررة"))
            if S["confirm"] and not messagebox.askyesno(APP_TITLE, T("نقل {0} ملف إلى «ملفات مكررة»؟").format(len(fs)), parent=win):
                return
            self.run_plan([(f["path"], dest) for f in fs])
            refresh_after({f["path"] for f in fs})

        def trash_sel():
            fs = sel_files()
            if fs and self.trash_selected(fs, parent=win):
                refresh_after({f["path"] for f in fs})

        def refresh_after(gone):
            st["groups"] = [[f for f in g if f["path"] not in gone] for g in st["groups"]]
            st["groups"] = [g for g in st["groups"] if len(g) > 1]
            render()

        bot = ttk.Frame(win, padding=10)
        bot.pack(fill="x")
        ttk.Button(bot, text=T("✔ حدد النسخ الزايدة (خلّي الأصلية)"), command=auto_select).pack(side=SR, padx=3)
        ttk.Button(bot, text=T("📦 انقل المحدد لمجلد «ملفات مكررة»"), style="Accent.TButton", command=move_sel).pack(side=SL, padx=3)
        ttk.Button(bot, text=T("🗑 لسلة المحذوفات"), command=trash_sel).pack(side=SL, padx=3)

        def work():
            def prog(d, t):
                win.after(0, lambda: (pb.configure(maximum=max(t, 1), value=d),
                                      info.set(T("جارٍ مقارنة المحتوى... {0}/{1}").format(d, t))))
            groups = find_exact_duplicates(list(self.files), prog)
            win.after(0, lambda: (st.__setitem__("groups", groups), pb.configure(value=pb["maximum"]), render()))
        threading.Thread(target=work, daemon=True).start()

    # ---------- الصور المتشابهة
    def similar_dialog(self):
        try:
            from PIL import Image, ImageTk  # noqa
        except ImportError:
            messagebox.showwarning(APP_TITLE, T("هالميزة بتحتاج مكتبة Pillow.\nهي موجودة جوّا نسخة الـ EXE، أو نزّلها بالأمر:\npip install pillow"))
            return
        if not self.files:
            messagebox.showwarning(APP_TITLE, T("افحص مجلداً أولاً."))
            return
        from PIL import Image, ImageTk
        win = self._dialog(T("الصور المتشابهة"), "1150x760")
        win.grab_release()
        level = tk.StringVar(value=SIMILAR_LEVELS[1][0])
        scope = tk.StringVar(value="all")
        info = tk.StringVar(value=T("اختار درجة التشابه واكبس «ابحث»."))
        st = {"groups": [], "vars": {}, "thumbs": [], "busy": False}

        top = ttk.Frame(win, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text=T("درجة التشابه:")).pack(side=SR)
        ttk.Combobox(top, textvariable=level, state="readonly", width=20, justify=JR,
                     values=[l[0] for l in SIMILAR_LEVELS]).pack(side=SR, padx=6)
        ttk.Radiobutton(top, text=T("كل الصور"), value="all", variable=scope).pack(side=SR, padx=(12, 2))
        ttk.Radiobutton(top, text=T("المعروضة بس"), value="filtered", variable=scope).pack(side=SR, padx=2)
        go = ttk.Button(top, text=T("🔍 ابحث"), style="Accent.TButton")
        go.pack(side=SR, padx=10)
        pb = ttk.Progressbar(top, length=200, mode="determinate")
        pb.pack(side=SL)
        ttk.Label(win, textvariable=info, style="Muted.TLabel", padding=(12, 0)).pack(anchor=AE)

        mid = ttk.Frame(win)
        mid.pack(fill="both", expand=True, padx=10, pady=6)
        canvas = tk.Canvas(mid, bg=BG, highlightthickness=0)
        vs = ttk.Scrollbar(mid, command=canvas.yview)
        canvas.configure(yscrollcommand=vs.set)
        vs.pack(side=SR, fill="y")
        canvas.pack(side=SL, fill="both", expand=True)
        inner = ttk.Frame(canvas)
        inner_id = canvas.create_window(0, 0, window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(inner_id, width=e.width))

        def wheel(e):
            canvas.yview_scroll(int(-e.delta / 120) if e.delta else (1 if e.num == 5 else -1), "units")
        win.bind("<MouseWheel>", wheel)
        win.bind("<Button-4>", wheel)
        win.bind("<Button-5>", wheel)

        bot = ttk.Frame(win, padding=10)
        bot.pack(fill="x")

        def selected_items():
            return [it for g in st["groups"] for it in g if st["vars"].get(it["path"]) and st["vars"][it["path"]].get()]

        def update_info():
            sel = selected_items()
            n = sum(len(g) for g in st["groups"])
            info.set(T("{0} مجموعة  •  {1} صورة متشابهة  •  المحدد: {2} ({3})").format(len(st['groups']), n, len(sel), human(sum(i['size'] for i in sel))))

        def auto_select():
            for g in st["groups"]:
                for k, it in enumerate(g):
                    st["vars"][it["path"]].set(k > 0)
            update_info()

        def clear_sel():
            for v in st["vars"].values():
                v.set(False)
            update_info()

        def move_dups(ask_folder):
            sel = selected_items()
            if not sel:
                messagebox.showinfo(APP_TITLE, T("حدد الصور اللي بدك تنقلها أولاً."), parent=win)
                return
            if ask_folder:
                d = filedialog.askdirectory(parent=win, initialdir=self.root_dir.get())
                if not d:
                    return
                dest = os.path.normpath(d)
            else:
                dest = os.path.join(self.root_dir.get(), T("صور مكررة"))
            if S["confirm"] and not messagebox.askyesno(
                    APP_TITLE, T("نقل {0} صورة ({1}) إلى:\n{2} ؟\n(بتقدر تتراجع بعدين)").format(len(sel), human(sum(i['size'] for i in sel)), dest), parent=win):
                return
            self.run_plan([(it["path"], dest) for it in sel])
            gone = {it["path"] for it in sel}
            st["groups"] = [[it for it in g if it["path"] not in gone] for g in st["groups"]]
            st["groups"] = [g for g in st["groups"] if len(g) > 1]
            render()

        ttk.Button(bot, text=T("✔ حدد المكرر تلقائياً (خلّي الأفضل)"), command=auto_select).pack(side=SR, padx=3)
        ttk.Button(bot, text=T("✖ إلغاء التحديد"), command=clear_sel).pack(side=SR, padx=3)
        ttk.Button(bot, text=T("📦 انقل المحدد لمجلد «صور مكررة»"), style="Accent.TButton",
                   command=lambda: move_dups(False)).pack(side=SL, padx=3)
        ttk.Button(bot, text=T("📦 انقل المحدد إلى..."), command=lambda: move_dups(True)).pack(side=SL, padx=3)

        def render():
            for w in inner.winfo_children():
                w.destroy()
            st["thumbs"].clear()
            old = st["vars"]
            st["vars"] = {}
            if not st["groups"]:
                ttk.Label(inner, text=T("ما في صور متشابهة 👌"), font=F(13)).pack(pady=40)
                update_info()
                return
            cols = max(2, (canvas.winfo_width() - 30) // 175)
            for gi, g in enumerate(st["groups"][:300], 1):
                box = ttk.Frame(inner, style="Panel.TFrame", padding=10)
                box.pack(fill="x", pady=5)
                waste = sum(it["size"] for it in g[1:])
                ttk.Label(box, text=T("مجموعة {0}  —  {1} صور  •  بتوفّر {2}").format(gi, len(g), human(waste)),
                          style="Panel.TLabel", font=F(11, True), foreground=ACCENT).pack(anchor=AE, pady=(0, 6))
                cards = ttk.Frame(box, style="Panel.TFrame")
                cards.pack(anchor=AE)
                for k, it in enumerate(g):
                    card = tk.Frame(cards, bg=FIELD, highlightthickness=2,
                                    highlightbackground=ACCENT if k == 0 else LINE)
                    card.grid(row=1 + k // cols, column=cols - 1 - k % cols, padx=5, pady=5, sticky="n")
                    ph = ImageTk.PhotoImage(it["thumb"]) if it.get("thumb") else None
                    st["thumbs"].append(ph)
                    lb = tk.Label(card, image=ph, bg=FIELD, width=160, height=130, cursor="hand2")
                    lb.pack(padx=4, pady=4)
                    lb.bind("<Double-1>", lambda e, p=it["path"]: open_path(p))
                    v = tk.BooleanVar(value=old[it["path"]].get() if it["path"] in old else False)
                    v.trace_add("write", lambda *_: update_info())
                    st["vars"][it["path"]] = v
                    tk.Checkbutton(card, text=it["name"][:22], variable=v, bg=FIELD, fg=FG,
                                   selectcolor=FIELD, activebackground=FIELD, activeforeground=FG,
                                   font=F(9), anchor=AE).pack(fill="x", padx=4)
                    meta = f"{it['w']}×{it['h']}  •  {human(it['size'])}"
                    tk.Label(card, text=(T("⭐ الأفضل  •  ") if k == 0 else "") + meta, bg=FIELD,
                             fg=ACCENT if k == 0 else MUTED, font=F(8)).pack(padx=4)
                    rel = os.path.relpath(os.path.dirname(it["path"]), self.root_dir.get())
                    tk.Label(card, text=f"📁 {rel}"[:28], bg=FIELD, fg=MUTED, font=F(8)).pack(padx=4, pady=(0, 4))
            if len(st["groups"]) > 300:
                ttk.Label(inner, text=T("معروض أول 300 مجموعة."), style="Muted.TLabel").pack(pady=6)
            canvas.yview_moveto(0)
            update_info()

        def search():
            if st["busy"]:
                return
            st["busy"] = True
            go.state(["disabled"])
            src = self.files if scope.get() == "all" else self.filtered
            imgs = [f for f in src if f["ext"].lower() in HASHABLE]
            thr = dict(SIMILAR_LEVELS)[level.get()]
            info.set(T("جارٍ تحليل {0} صورة...").format(len(imgs)))
            pb.configure(maximum=max(1, len(imgs)), value=0)

            def prog(v, txt):
                win.after(0, lambda: (pb.configure(value=v), info.set(txt)))

            def work():
                items = []
                for k, f in enumerate(imgs):
                    try:
                        h, (w, hh) = image_fingerprint(f["path"])
                        items.append({**f, "hash": h, "w": w, "h": hh})
                    except Exception:  # noqa
                        pass
                    if k % 20 == 0:
                        prog(k, T("جارٍ تحليل الصور... {0}/{1}").format(k, len(imgs)))
                prog(len(imgs), T("جارٍ مقارنة الصور..."))
                groups = group_similar(items, thr)
                for g in groups[:300]:
                    for it in g:
                        try:
                            with Image.open(it["path"]) as im:
                                im.draft("RGB", (320, 260))
                                t = im.convert("RGB")
                                t.thumbnail((160, 130))
                                it["thumb"] = t
                        except Exception:  # noqa
                            it["thumb"] = None
                win.after(0, lambda: done(groups))

            def done(groups):
                st["busy"] = False
                go.state(["!disabled"])
                st["groups"] = groups
                render()

            threading.Thread(target=work, daemon=True).start()

        go.config(command=search)
        win.after(200, search)

    # ---------- التنظيم التلقائي
    def organize_dialog(self):
        root = self.root_dir.get()
        if not self.files or not os.path.isdir(root):
            messagebox.showwarning(APP_TITLE, T("افحص مجلداً أولاً."))
            return
        win = self._dialog(T("تنظيم تلقائي"), "640x560")
        mode = tk.StringVar(value=S["default_mode"])
        scope = tk.StringVar(value="all")
        dest = tk.StringVar(value=root)

        frm = ttk.Frame(win, padding=14)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=T("طريقة التنظيم:"), style="Title.TLabel").pack(anchor=AE)
        for val, txt in ORGANIZE_MODES:
            ttk.Radiobutton(frm, text=txt, value=val, variable=mode, command=lambda: update()).pack(anchor=AE, padx=10)

        ttk.Label(frm, text=T("الملفات:"), style="Title.TLabel").pack(anchor=AE, pady=(10, 0))
        ttk.Radiobutton(frm, text=T("كل الملفات ({0})").format(len(self.files)), value="all",
                        variable=scope, command=lambda: update()).pack(anchor=AE, padx=10)
        ttk.Radiobutton(frm, text=T("الملفات المعروضة حالياً فقط ({0})").format(len(self.filtered)), value="filtered",
                        variable=scope, command=lambda: update()).pack(anchor=AE, padx=10)

        drow = ttk.Frame(frm)
        drow.pack(fill="x", pady=(10, 0))
        ttk.Label(drow, text=T("المجلدات الجديدة تنعمل داخل:")).pack(side=SR)

        def pick_dest():
            d = filedialog.askdirectory(parent=win, initialdir=dest.get())
            if d:
                dest.set(os.path.normpath(d))
                update()
        ttk.Button(drow, text=T("تغيير"), command=pick_dest).pack(side=SL)
        ttk.Entry(drow, textvariable=dest, state="readonly").pack(side=SR, fill="x", expand=True, padx=4)

        ttk.Label(frm, text=T("معاينة (المجلد ← عدد الملفات):"), style="Title.TLabel").pack(anchor=AE, pady=(10, 2))
        preview = dark_listbox(frm, height=9, justify=JR)
        preview.pack(fill="both", expand=True)

        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(10, 0))
        state = {"plan": []}

        def update():
            files = self.files if scope.get() == "all" else self.filtered
            plan = plan_organize(files, dest.get(), mode.get())
            state["plan"] = plan
            counts = {}
            for _src, d in plan:
                rel = os.path.relpath(d, dest.get())
                counts[rel] = counts.get(rel, 0) + 1
            preview.delete(0, "end")
            if not plan:
                preview.insert("end", T("كل شي منظم، ما في ملفات بدها نقل 👌"))
            for rel, n in sorted(counts.items(), key=lambda kv: -kv[1]):
                preview.insert("end", T("{0}   ←   {1} ملف").format(rel, n))
            go.config(text=T("تنفيذ ونقل {0} ملف").format(len(plan)))

        def run():
            if not state["plan"]:
                return
            if (not S["confirm"]) or messagebox.askyesno(
                    APP_TITLE, T("متأكد؟ رح ينقل {0} ملف.\n(بتقدر تتراجع بعدين)").format(len(state['plan'])), parent=win):
                win.destroy()
                self.run_plan(state["plan"])

        go = ttk.Button(btns, text=T("تنفيذ"), style="Accent.TButton", command=run)
        go.pack(side=SR)
        ttk.Button(btns, text=T("إلغاء"), command=win.destroy).pack(side=SL)
        update()


def main():
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GraphicWO.FileOrganizer")
        except Exception:  # noqa
            pass
    load_private_fonts()
    app = App()
    app.after(2500, lambda: check_for_update(app))
    app.mainloop()


def _ver(v):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except Exception:
        return (0,)


def check_for_update(root):
    """يتأكد بالخلفية إذا في نسخة أحدث، وإذا في بيسأل المستخدم."""
    def work():
        try:
            import urllib.request
            req = urllib.request.Request(UPDATE_URL, headers={"Cache-Control": "no-cache", "User-Agent": "GraphicWO-Organizer"})
            with urllib.request.urlopen(req, timeout=8) as r:
                info = json.loads(r.read().decode("utf-8")).get("organizer", {})
            latest = str(info.get("version", ""))
            if latest and _ver(latest) > _ver(APP_VERSION):
                notes = info.get("notes_" + LANG) or info.get("notes_ar") or ""
                root.after(0, lambda: ask(latest, notes, info.get("url") or DOWNLOAD_URL))
        except Exception:
            pass

    def ask(latest, notes, url):
        if messagebox.askyesno(T("🎉 في تحديث جديد"), T("في نسخة جديدة من البرنامج ({0}).\nنسختك: {1}\n\n{2}\n\nبدك تنزّلها هلق؟").format(latest, APP_VERSION, notes), parent=root):
            webbrowser.open(url)

    threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    main()
