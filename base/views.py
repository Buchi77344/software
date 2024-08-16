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

from docx import Document
from docx.oxml import OxmlElement
from io import BytesIO
import os

def upload(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            try:
                if not file.name.endswith('.docx'):
                    messages.error(request, 'Please upload a DOCX file.')
                    return redirect('upload')

                document = Document(file)
                question_text = None
                options = []
                correct_option = None
                diagram_path = None

                for para in document.paragraphs:
                    text = para.text.strip()

                    # Check for question section
                    if text.startswith("Q:"):
                        if question_text:
                            save_question_and_answers(question_text, options, correct_option, diagram_path)
                            options = []
                            diagram_path = None

                        question_text = text.replace("Q:", "").strip()

                    # Check for diagram section
                    elif text.startswith("D:"):
                        # Process diagrams or shapes
                        diagram_path = process_diagram(document)

                    # Check for correct option
                    elif text.startswith("Correct:"):
                        correct_option = int(text.replace("Correct:", "").strip())

                    # Check for options
                    elif text.startswith("1.") or text.startswith("2.") or text.startswith("3.") or text.startswith("4."):
                        options.append(text.strip())

                # Handle remaining question data after the loop
                if question_text:
                    save_question_and_answers(question_text, options, correct_option, diagram_path)

                messages.success(request, "Questions and answers uploaded successfully!")
                return redirect('/')

            except Exception as e:
                messages.error(request, f"Error processing the file: {e}")
                return redirect('upload')

    else:
        form = BulkUploadForm()

    return render(request, 'upload.html', {'form': form})

def save_question_and_answers(question_text, options, correct_option, diagram_path):
    question, created = Question.objects.get_or_create(text=question_text)

    if diagram_path:
        question.diagram = diagram_path
        question.save()

    for i, option_text in enumerate(options, 1):
        is_correct = (i == correct_option)
        Answer.objects.create(question=question, text=option_text, is_correct=is_correct)

def process_diagram(document):
    for shape in document.inline_shapes:
        if shape.type == 3:  # Type 3 corresponds to images
            image = shape.image
            image_stream = BytesIO(image.blob)
            image_filename = save_image(image_stream)
            return f'questions/diagrams/{image_filename}'
    return None

def save_image(image_stream):
    # Save image to the file system and return the filename
    image_filename = 'diagram.png'
    image_path = os.path.join('media', 'questions', 'diagrams', image_filename)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    with open(image_path, 'wb') as f:
        f.write(image_stream.read())
    return image_filename
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




