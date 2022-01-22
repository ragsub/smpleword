import json
from django.shortcuts import render
from wordle.forms import WordleForm, WordForm, AlphabetForm
from django.forms.formsets import formset_factory
from django.contrib import messages
from wordle.settings import BASE_DIR
import os
from cryptography.fernet import Fernet
import random

ENCODING_FORMAT = 'utf8'

def help_menu(request):
    return render(
        request=request, 
        template_name="wordle/help.html", 
    ) 

def process_word(request):

    MAX_ATTEMPTS = 6
    five_letter_words = os.path.join(BASE_DIR, 'static', '5-letter-words.json')
    en_dict = json.load(open(five_letter_words))
    en_list = [en['word'] for en in en_dict]
    SECRET_KEY = bytes(os.getenv('ENCRYPTION_KEY', None),ENCODING_FORMAT)
    f = Fernet(SECRET_KEY)

    
    context={}
    WordFormSet = formset_factory(WordForm, extra=6, max_num=6)
    AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)


    if request.method == 'POST':
        words = WordFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='word')
        form = WordleForm(request.POST.copy())
        alphabets = AlphabetFormSet(request.POST.copy(), form_kwargs={'empty_permitted':False}, prefix='alphabet')
    
        if words.is_valid() & form.is_valid() & alphabets.is_valid():
            TARGET_WORD = f.decrypt(bytes(form.cleaned_data['target_word'],ENCODING_FORMAT)).decode()

            entered_word = form.cleaned_data['word'].lower()
            attempts_left = form.cleaned_data['attempts_left']
            attempts = MAX_ATTEMPTS - attempts_left
            form.data['word'] = ""

            if attempts_left > 0:
            
                if entered_word in en_list:
                    attempts = attempts + 1
                    form.data['attempts_left'] = attempts_left-1
                    i = 0
                    for word in words:
                        i = i+1
                        if i==attempts:
                            word.cleaned_data['w']= entered_word
                        
                            for j in range (0,5):
                                letter = 'l'+str(j+1)
                                if entered_word[j] == TARGET_WORD[j]:
                                    word.cleaned_data[letter] = 'bg-success'
                                    alphabets[ord(entered_word[j])-97].cleaned_data['letter'] = 'btn-success'
                                elif entered_word[j] in TARGET_WORD:
                                    word.cleaned_data[letter] = 'bg-warning'
                                    if alphabets[ord(entered_word[j])-97].cleaned_data['letter'] != 'btn-success': 
                                        alphabets[ord(entered_word[j])-97].cleaned_data['letter'] = 'btn-warning'
                                else:
                                    word.cleaned_data[letter] = 'bg-secondary'
                                    alphabets[ord(entered_word[j])-97].cleaned_data['letter'] = 'btn-secondary'

                            break
                    
                    new_words = WordFormSet(initial = words.cleaned_data, prefix='word')
                    new_alphabets = AlphabetFormSet(initial = alphabets.cleaned_data, prefix="alphabet")
                    context['words'] = new_words
                    context['form'] = form
                    context['alphabets'] = new_alphabets
                    
                    if entered_word == TARGET_WORD:
                        messages.add_message(request=request, level=messages.SUCCESS, message='You solved it in '+ str(attempts) + ' attempts! Challenge your friend by clicking '+'<a href='+request.path+'?target_word='+form.cleaned_data['target_word']+'>here</a>', extra_tags='safe')
                        form.fields['word'].widget.attrs.update({'readonly':'readonly'})

                    if attempts_left == 1:
                        messages.add_message(request=request, level=messages.ERROR, message = 'Chances over. word is '+TARGET_WORD)

                else:
                    messages.add_message(request=request, level=messages.ERROR, message=entered_word+' is not a valid english word')
                    context['words'] = words
                    context['form'] = form
                    context['alphabets'] = alphabets
            else:
                messages.add_message(request=request, level=messages.ERROR, message = 'Chances over. word is '+TARGET_WORD)
                context['words'] = words
                context['form'] = form
                context['alphabets'] = alphabets
        else:
            print(form.errors)
            print(form.non_field_errors)
            print(words.errors)
            print(words.non_form_errors())    
    else:    
        form = WordleForm()
        words = WordFormSet(prefix='word')
        alphabets = AlphabetFormSet(prefix='alphabet')

        if request.GET.get('target_word',None) == None:
            target_word = random.choice(en_list)
            encrypted_word = f.encrypt(bytes(target_word, ENCODING_FORMAT))
            form.fields['target_word'].initial = encrypted_word.decode()
        else:
            request.GET._mutable = True
            encrypted_word = request.GET.get('target_word')
            form.fields['target_word'].initial = encrypted_word
            request.GET['target_word'] = None


        context['words'] = words
        context['form'] = form
        context['alphabets'] = alphabets
    
    return render(
        request=request, 
        template_name="wordle/wordle1.html", 
        context = context
    ) 