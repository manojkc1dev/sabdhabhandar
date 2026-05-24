from django.db import models

class DictionaryWord(models.Model):
    # This column stores the English word. 'unique=True' prevents duplicate entries.
    english_word = models.CharField(max_length=100, unique=True)
    
    # This column stores the Nepali translations (e.g., "Buwa, Baba")
    nepali_translation = models.CharField(max_length=255)

    # This makes the word show up nicely in the Django admin panel
    def __str__(self):
        return f"{self.english_word} -> {self.nepali_translation}"