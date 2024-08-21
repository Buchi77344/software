from django.shortcuts import render ,redirect ,get_object_or_404
import requests
import logging
from django.db import transaction
from .models import Userprofile ,Suffle ,Subject,ExamSession
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from uuid import uuid4
import uuid
from datetime import datetime
from django.urls import reverse

@login_required(login_url='login')
def index(request):
    subjects = Subject.objects.all()
    selected_subject_id = request.GET.get('subject_id')
    questions = []
    remaining_time = None
    selected_subject = None

    request.session['selected_subject_id'] = selected_subject_id

    if subjects.exists():
        if selected_subject_id:
            selected_subject = Subject.objects.get(id=selected_subject_id)
        else:
            selected_subject = subjects.first()

        # Fetch ExamSession related to the selected subject and shuffle the questions
        exam_sessions = ExamSession.objects.filter(subject=selected_subject).order_by('shuffle_order')
        questions = [session.question for session in exam_sessions]

        if request.method == 'POST':
            results = []
            for question in questions:
                selected_answer_id = request.POST.get(f'question_{question.id}')
                if selected_answer_id:
                    selected_answer = question.answers.get(id=selected_answer_id)
                    is_correct = selected_answer.is_correct
                else:
                    selected_answer = None
                    is_correct = False

                # Save result to the Result model
                result = Result(
                    user=request.user,
                    subject=selected_subject,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=is_correct,
                    score=1.0 if is_correct else 0.0
                )
                result.save()

                results.append({
                    'question_id': question.id,
                    'selected_answer_id': selected_answer.id if selected_answer else None,
                    'correct': is_correct
                })

            # Redirect to the result page
            return redirect(reverse('result') + f'?subject_id={selected_subject_id}')

        # Shuffle questions
        seed = request.session.get(f'shuffle_seed_{selected_subject.id}')
        if not seed:
            seed = timezone.now().timestamp()
            request.session[f'shuffle_seed_{selected_subject.id}'] = seed

        random.seed(seed)
        random.shuffle(questions)

        # Calculate remaining time for the exam
        if exam_sessions.exists():
            start_time = exam_sessions.first().exam_start_time
            duration = exam_sessions.first().exam_duration
            hours, minutes, seconds = map(int, duration.split(':'))
            end_time = start_time + timezone.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            remaining_time = max(0, (end_time - timezone.now()).total_seconds())

    return render(request, 'index.html', {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'questions': questions,
        'remaining_time': remaining_time,
    })
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
from .models import Question, Answer ,Result








@login_required(login_url='login')
def result(request):
    
    # if not subject_id:
    #     return redirect('index')  # Redirect to index if no subject_id is provided
    
    
    user_results = Result.objects.filter(user=request.user)

    # Calculate scores
    total_questions = user_results.count()
    correct_answers = user_results.filter(is_correct=True).count() 
    
    return render(request, 'result.html', {
      
        'user_results': user_results,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
    })
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




def userpage(request):
    return render(request, 'user-page.html')