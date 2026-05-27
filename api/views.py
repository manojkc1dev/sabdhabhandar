import os
import csv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DictionaryWord

# --- Auto-Import Logic ---
def import_csv_if_needed():
    """Checks if the database is empty and populates it from words.csv if necessary."""
    try:
        if DictionaryWord.objects.count() == 0:
            file_path = os.path.join(settings.BASE_DIR, 'words.csv')
            if os.path.exists(file_path):
                print(f"DEBUG: Empty database found. Importing from {file_path}")
                # Use utf-8-sig to automatically remove invisible BOM characters
                with open(file_path, mode='r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    words = []
                    for row in reader:
                        # Aggressively strip spaces, newlines, and hidden quotes
                        eng = row['english_word'].strip(' \t\n\r"\'').lower()
                        nep = row['nepali_translation'].strip(' \t\n\r"\'')
                        words.append(DictionaryWord(english_word=eng, nepali_translation=nep))
                    
                    DictionaryWord.objects.bulk_create(words)
                    print("DEBUG: Import successful!")
            else:
                print(f"DEBUG ERROR: words.csv not found at {file_path}")
    except Exception as e:
        print(f"DEBUG ERROR: Import failed with: {str(e)}")

# --- API View for Search ---
class TranslateWordAPI(APIView):
    def get(self, request):
        word = request.query_params.get('word', '').strip(' \t\n\r"\'').lower()
        if not word:
            return Response({"error": "No word provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # .filter(__iexact) makes it case-insensitive and safe from crashes
        db_word = DictionaryWord.objects.filter(english_word__iexact=word).first()
        
        if db_word:
            history = request.session.get('recent_searches', [])
            if db_word.english_word not in history:
                history.insert(0, db_word.english_word)
                request.session['recent_searches'] = history[:5]
                request.session.modified = True 
            
            return Response({
                "english_word": db_word.english_word,
                "nepali_translation": db_word.nepali_translation
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Word not found"}, status=status.HTTP_404_NOT_FOUND)

# --- Debugging View ---
def debug_db(request):
    return HttpResponse(f"Database contains {DictionaryWord.objects.count()} words.")

# --- Standard Views ---
def homepage(request):
    import_csv_if_needed() # Ensure database is populated
    random_word = DictionaryWord.objects.order_by('?').first()
    recent_searches = request.session.get('recent_searches', [])
    context = {
        'random_word': random_word,
        'recent_searches': recent_searches
    }
    return render(request, 'index.html', context)

def translate_view(request):
    word = request.GET.get('word', '').strip(' \t\n\r"\'').lower()
    
    if not word:
        return JsonResponse({'error': 'No word provided'}, status=400)

    # .filter().first() gracefully returns None if missing, instead of crashing!
    db_word = DictionaryWord.objects.filter(english_word__iexact=word).first()
    
    if db_word:
        history = request.session.get('recent_searches', [])
        if db_word.english_word not in history:
            history.insert(0, db_word.english_word)
            request.session['recent_searches'] = history[:5]
            request.session.modified = True 

        return JsonResponse({
            'english_word': db_word.english_word,
            'nepali_translation': db_word.nepali_translation
        })
    else:
        return JsonResponse({'error': 'Word not found in dictionary'}, status=404)
    
def privacy_policy(request):
    return render(request, 'privacy.html')