import os
import csv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DictionaryWord

def import_csv_if_needed():
    try:
        if DictionaryWord.objects.count() == 0:
            file_path = os.path.join(settings.BASE_DIR, 'words.csv')
            if os.path.exists(file_path):
                with open(file_path, mode='r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    words = []
                    for row in reader:
                        eng = row['english_word'].strip(' \t\n\r"\'').lower()
                        nep = row['nepali_translation'].strip(' \t\n\r"\'')
                        if eng and nep:
                            words.append(DictionaryWord(english_word=eng, nepali_translation=nep))
                    DictionaryWord.objects.bulk_create(words)
    except Exception:
        pass

def get_word_safely(search_word):
    """BULLETPROOF SEARCH: Bypasses SQLite unicode bugs by forcing a raw Python match."""
    if not search_word: return None
    
    # 1. Try standard fast lookup
    db_word = DictionaryWord.objects.filter(english_word__iexact=search_word).first()
    if db_word: return db_word
    
    # 2. Fallback: Force a manual scan of the database to strip all invisible characters
    for w in DictionaryWord.objects.all():
        clean_db = w.english_word.replace('\ufeff', '').replace('\u200b', '').strip().lower()
        clean_search = search_word.replace('\ufeff', '').replace('\u200b', '').strip().lower()
        if clean_db == clean_search and clean_search != '':
            return w
            
    return None

def homepage(request):
    import_csv_if_needed()
    random_word = DictionaryWord.objects.order_by('?').first()
    recent_searches = request.session.get('recent_searches', [])
    return render(request, 'index.html', {
        'random_word': random_word,
        'recent_searches': recent_searches
    })

def translate_view(request):
    word = request.GET.get('word', '').strip().lower()
    if not word:
        return JsonResponse({'error': 'No word provided'}, status=400)

    # Use our unbreakable search function
    db_word = get_word_safely(word)
    
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
    
    return JsonResponse({'error': 'Word not found in dictionary'}, status=404)

class TranslateWordAPI(APIView):
    def get(self, request):
        word = request.query_params.get('word', '').strip().lower()
        db_word = get_word_safely(word)
        if db_word:
            return Response({
                "english_word": db_word.english_word,
                "nepali_translation": db_word.nepali_translation
            }, status=status.HTTP_200_OK)
        return Response({"error": "Word not found"}, status=status.HTTP_404_NOT_FOUND)

def debug_db(request):
    return HttpResponse(f"Database contains {DictionaryWord.objects.count()} words.")

def privacy_policy(request):
    return render(request, 'privacy.html')