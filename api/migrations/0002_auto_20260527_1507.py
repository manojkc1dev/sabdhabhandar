# ... existing imports ...
import os
from django.conf import settings

def load_data(apps, schema_editor):
    DictionaryWord = apps.get_model('api', 'DictionaryWord')
    
    # Force the path to be the root of your project
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, 'words.csv')
    
    # ... rest of your import logic ...