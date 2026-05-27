import os
from django.conf import settings
from django.db import migrations
import csv

def load_data(apps, schema_editor):
    DictionaryWord = apps.get_model('api', 'DictionaryWord')
    # Use BASE_DIR to find the file regardless of where the script runs
    file_path = os.path.join(settings.BASE_DIR, 'words.csv')
    
    if os.path.exists(file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                DictionaryWord.objects.get_or_create(
                    english_word=row['english_word'].lower().strip(),
                    nepali_translation=row['nepali_translation'].strip()
                )
    else:
        # This print will appear in your Render Build Logs
        print(f"DEBUG: Could not find CSV at {file_path}")

class Migration(migrations.Migration):
    dependencies = [('api', '0001_initial')]
    operations = [migrations.RunPython(load_data)]