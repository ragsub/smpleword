from django.shortcuts import render
from wordle.forms import WordleForm, WordForm, AlphabetForm
from django.forms.formsets import formset_factory
from django.contrib import messages

import enchant


MAX_ATTEMPTS = 6
TARGET_WORD = 'manor'

def process_word(request):
    context={}
    WordFormSet = formset_factory(WordForm, extra=6, max_num=6)
    AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)
    
    if request.method == 'POST':
        words = WordFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='word')
        form = WordleForm(request.POST.copy())
        alphabets = AlphabetFormSet(request.POST.copy(), form_kwargs={'empty_permitted':False}, prefix='alphabet')
    
        if words.is_valid() & form.is_valid() & alphabets.is_valid():
            entered_word = form.cleaned_data['word'].lower()
            attempts_left = form.cleaned_data['attempts_left']
            attempts = MAX_ATTEMPTS - attempts_left
            form.data['word'] = ""
            
            dict = enchant.Dict('en_US')
            if dict.check(entered_word):
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
                                alphabets[ord(entered_word[j])-97].cleaned_data['letter'] = 'bg-success'
                            elif entered_word[j] in TARGET_WORD:
                                word.cleaned_data[letter] = 'bg-warning'
                                if alphabets[ord(entered_word[j])-97].cleaned_data['letter'] != 'bg-success': 
                                    alphabets[ord(entered_word[j])-97].cleaned_data['letter'] = 'bg-warning'
                            else:
                                word.cleaned_data[letter] = 'bg-secondary'
                                alphabets[ord(entered_word[j])-97].cleaned_data['letter'] = 'bg-secondary'

                        break
                
                #WordFormSet = formset_factory(WordForm, max_num=6, prefix="")
                new_words = WordFormSet(initial = words.cleaned_data, prefix='word')
                new_alphabets = AlphabetFormSet(initial = alphabets.cleaned_data, prefix="alphabet")
                context['words'] = new_words
                context['form'] = form
                context['alphabets'] = new_alphabets
                
                if entered_word == TARGET_WORD:
                    messages.add_message(request=request, level=messages.SUCCESS, message='That is right!')
                    form.fields['word'].widget.attrs.update({'readonly':'readonly'})
                elif attempts_left == 1:
                    form.fields['word'].widget.attrs.update({'readonly':'readonly'})
                    messages.add_message(request=request, level=messages.ERROR, message = 'Chances over. word is '+TARGET_WORD)
            else:
                messages.add_message(request=request, level=messages.ERROR, message=entered_word+' is not a valid english word')
                context['words'] = words
                context['form'] = form
        else:
            print(form.errors)
            print(form.non_field_errors)
            print(words.errors)
            print(words.non_form_errors())    
    else:    
        form = WordleForm()
        words = WordFormSet(prefix='word')
        alphabets = AlphabetFormSet(prefix='alphabet')
        
        form.data['max_attempts'] = 6
        context['words'] = words
        context['form'] = form
        context['alphabets'] = alphabets
    
    return render(
        request=request, 
        template_name="wordle/wordle.html", 
        context = context
    ) 