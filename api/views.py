from django.shortcuts import render
from rest_framework.views import APIView, settings
from rest_framework.response import Response
from rest_framework import status

import os
import pandas as pd
from django.http import JsonResponse

# Import your database model!
from .models import DictionaryWord 

class TranslateWordAPI(APIView):
    def get(self, request):
        # 1. Get the requested word from the URL
        word = request.query_params.get('word', None)

        if not word:
            return Response(
                {"error": "Please provide a word to translate. Example: ?word=hello"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Clean the input
        clean_word = word.lower().strip()

        # 3. Search the Database!
        try:
            # This looks for the exact word in your database table
            db_word = DictionaryWord.objects.get(english_word=clean_word)
            
            return Response({
                "english_word": db_word.english_word,
                "nepali_translation": db_word.nepali_translation
            }, status=status.HTTP_200_OK)

        except DictionaryWord.DoesNotExist:
            # If the database doesn't have it, return the error
            return Response({
                "english_word": clean_word,
                "error": "Not found in the dictionary"
            }, status=status.HTTP_404_NOT_FOUND)

def homepage(request):
    return render(request, 'index.html')

def translate_view(request):
    word = request.GET.get('word', '').lower()
    try:
        csv_path = os.path.join(settings.BASE_DIR, 'words.csv')
        df = pd.read_csv(csv_path, on_bad_lines='skip')
        
        # Ensure your column name matches exactly what is in your CSV
        result = df[df['english_word'] == word]
        
        if not result.empty:
            return JsonResponse({
                'english_word': word,
                'nepali_translation': result.iloc[0]['nepali_translation']
            })
        else:
            return JsonResponse({'error': 'Word not found in dictionary'}, status=404)
            
    except Exception as e:
        # This part MUST be indented to match the 'try'
        return JsonResponse({'error': str(e)}, status=500)