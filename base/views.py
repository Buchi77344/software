from django.shortcuts import render ,redirect
import requests
import logging
from django.db import transaction
from django.contrib.auth.decorators import login_required

# Configure logging

@login_required(login_url='login')
def index(request):
    questions =  Question.objects.prefetch_related('answers').all()

    context = {
        'questions': questions
    }
    return render(request, 'index.html',context)




import csv
import pandas as pd
from io import TextIOWrapper, StringIO
from django.shortcuts import render, redirect
from django.contrib import messages
from docx import Document
from .forms import BulkUploadForm
from .models import Question, Answer

import csv
from io import TextIOWrapper, StringIO
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BulkUploadForm
from .models import Question, Answer

def upload(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            csv_file = None

            try:
                # Check the file extension and read as CSV-like data
                if file.name.endswith('.txt'):
                    csv_file = TextIOWrapper(file.file, encoding=request.encoding)
                else:
                    messages.error(request, 'Unsupported file format. Please upload a .txt file.')
                    return redirect('upload')

                # Read the CSV-like data
                reader = csv.DictReader(csv_file)

                questions = []
                answers = []

                for row in reader:
                    question_text = row.get('question_text')
                    option1 = row.get('option1')
                    option2 = row.get('option2')
                    option3 = row.get('option3')
                    option4 = row.get('option4')
                    correct_option = row.get('correct_option')

                    if not (question_text and option1 and option2 and option3 and option4 and correct_option):
                        raise ValueError("Missing data in CSV file row.")

                    correct_option = int(correct_option)

                    # Create or get Question object
                    question, created = Question.objects.get_or_create(text=question_text)

                    # Create Answer objects
                    answers.append(Answer(question=question, text=option1, is_correct=(correct_option == 1)))
                    answers.append(Answer(question=question, text=option2, is_correct=(correct_option == 2)))
                    answers.append(Answer(question=question, text=option3, is_correct=(correct_option == 3)))
                    answers.append(Answer(question=question, text=option4, is_correct=(correct_option == 4)))

                # Bulk create answers
                Answer.objects.bulk_create(answers)

                messages.success(request, "Questions and answers uploaded successfully!")
                return redirect('/')

            except Exception as e:
                messages.error(request, f"Error uploading or processing file: {e}")
                return redirect('upload')

    else:
        form = BulkUploadForm()

    context = {'form': form}
    return render(request, 'upload.html', context)

def result(request):
    if request.method == 'POST':
        questions = Question.objects.prefetch_related('answers').all()
        total_questions = len(questions)
        correct_answers = 0
        user_responses = []

        for question in questions:
            answer_id = request.POST.get(f'question_{question.id}')
            selected_answer = Answer.objects.get(id=answer_id)

            if selected_answer.is_correct:
                correct_answers += 1

            correct_answer = question.answers.filter(is_correct=True).first()

            user_responses.append({
                'question': question,
                'selected_answer': selected_answer,
                'is_correct': selected_answer.is_correct,
                'correct_answer': correct_answer,
            })

        context = {
            'user_responses': user_responses,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
        }
        return render(request, 'result.html', context)

    else:
        return redirect('render_questions')

# views.py
import random
import string
from django.shortcuts import render
from .models import User
from .models import UserID
from .forms import UsernameForm
from django.db import IntegrityError, transaction

def generate_random_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def userid(request):
    error_message = None

    if request.method == "POST":
        form = UsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                with transaction.atomic():
                    user, created = User.objects.get_or_create(username=username)
                    if created:
                        user.set_password(User.objects.make_random_password())
                        user.save()
                    unique_id = generate_random_id()
                    while UserID.objects.filter(generated_id=unique_id).exists():
                        unique_id = generate_random_id()
                    user_id, created = UserID.objects.get_or_create(user=user)
                    user_id.generated_id = unique_id
                    user_id.save()
                    return redirect('userid')
            except IntegrityError:
                error_message = "There was an error creating the user. Please try again."
            except Exception as e:
                error_message = f"An unexpected error occurred: {str(e)}"
        else:
            error_message = "Invalid form data. Please correct the errors below."
    else:
        form = UsernameForm()

    return render(request, 'userid.html', {'form': form, 'error_message': error_message})
# views.py

from django.shortcuts import render, redirect
from django.contrib import auth
from .forms import LoginForm

def login(request):
    error_message = None

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            user = auth.authenticate(request, username=user_id)
            if user is not None:
                auth.login(request, user)
                return redirect('/')  # Redirect to a success page
            else:
                error_message = "Invalid user ID"
    else:
        form = LoginForm()
 
    return render(request, 'login.html', {'form': form, 'error_message': error_message})




