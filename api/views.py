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
    """Safely populates database with stripped values if completely empty."""
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

def homepage(request):
    import_csv_if_needed()
    for w in DictionaryWord.objects.all():
        clean_eng = w.english_word.replace('\ufeff', '').strip(' \t\n\r"\'').lower()
        if w.english_word != clean_eng:
            w.english_word = clean_eng
            w.save()
    # -----------------------------------------------------------

    random_word = DictionaryWord.objects.order_by('?').first()
    recent_searches = request.session.get('recent_searches', [])
    context = {
        'random_word': random_word,
        'recent_searches': recent_searches
    }
    return render(request, 'index.html', context)

def translate_view(request):
    """Handles frontend fetch requests seamlessly without crashing."""
    word = request.GET.get('word', '').strip(' \t\n\r"\'').lower()
    
    if not word:
        return JsonResponse({'error': 'No word provided'}, status=400)

    # filter + iexact completely eliminates trailing hidden formatting errors
    db_word = DictionaryWord.objects.filter(english_word__iexact=word).first()
    
    if db_word:
        # Save to session history
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
    """Fallback handler for standard DRF API endpoints."""
    def get(self, request):
        word = request.query_params.get('word', '').strip(' \t\n\r"\'').lower()
        db_word = DictionaryWord.objects.filter(english_word__iexact=word).first()
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