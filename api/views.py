import os, csv
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DictionaryWord

class TranslateWordAPI(APIView):
    def get(self, request):
        word = request.query_params.get('word', None)
        if not word:
            return Response({"error": "No word provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        clean_word = word.lower().strip()
        
        try:
            db_word = DictionaryWord.objects.get(english_word=clean_word)
            
            
            history = request.session.get('recent_searches', [])
            if clean_word not in history:
                history.insert(0, clean_word)
                request.session['recent_searches'] = history[:5]
                request.session.modified = True 
            
            return Response({
                "english_word": db_word.english_word,
                "nepali_translation": db_word.nepali_translation
            }, status=status.HTTP_200_OK)
            
        except DictionaryWord.DoesNotExist:
            return Response({"error": "Word not found"}, status=status.HTTP_404_NOT_FOUND)

def homepage(request):
    random_word = DictionaryWord.objects.order_by('?').first()
    
    recent_searches = request.session.get('recent_searches', [])
    
    print("DEBUG HOMEPAGE: Loading page. Current session history is:", recent_searches)

    context = {
        'random_word': random_word,
        'recent_searches': recent_searches
    }
    return render(request, 'index.html', context)

def translate_view(request):
    word = request.GET.get('word', '').lower().strip()
    
    if not word:
        return JsonResponse({'error': 'No word provided'}, status=400)

    try:
        db_word = DictionaryWord.objects.get(english_word=word)
        
        history = request.session.get('recent_searches', [])
        if word not in history:
            history.insert(0, word)
            request.session['recent_searches'] = history[:5]
            request.session.modified = True 
        
        print(f"DEBUG TRANSLATE: User translated '{word}'. Saved history is now: {request.session['recent_searches']}")

        return JsonResponse({
            'english_word': db_word.english_word,
            'nepali_translation': db_word.nepali_translation
        })
        
    except DictionaryWord.DoesNotExist:
        return JsonResponse({'error': 'Word not found in dictionary'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def privacy_policy(request):
    return render(request, 'privacy.html')



from django.http import HttpResponse
from api.models import DictionaryWord

def debug_db(request):
    count = DictionaryWord.objects.count()
    return HttpResponse(f"Database contains {count} words.")

def import_csv_if_needed():
    if DictionaryWord.objects.count() == 0:
        file_path = os.path.join(settings.BASE_DIR, 'words.csv')
        if os.path.exists(file_path):
            print("DEBUG: Database is empty. Starting import...")
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                words = [DictionaryWord(english_word=row['english_word'].lower().strip(), 
                                        nepali_translation=row['nepali_translation'].strip()) 
                         for row in reader]
                DictionaryWord.objects.bulk_create(words)
                print("DEBUG: CSV Import successful!")
        else:
            print(f"DEBUG ERROR: Could not find words.csv at {file_path}")