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
def userpage(request):
    subjects = Subject.objects.all()
    selected_subject_id = request.GET.get('subject_id')
    questions = []
    remaining_time = None
    selected_subject = None
    user_answers = []
    total_questions = 0

    request.session['selected_subject_id'] = selected_subject_id

    if subjects.exists():
        if selected_subject_id:
            selected_subject = Subject.objects.get(id=selected_subject_id)
        else:
            selected_subject = subjects.first()

        # Fetch ExamSession related to the selected subject and shuffle the questions
        exam_sessions = ExamSession.objects.filter(subject=selected_subject).order_by('shuffle_order')
        questions = [session.question for session in exam_sessions]

        # Count the total number of questions
        total_questions = len(questions)

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
            return redirect('login')

        # Retrieve user's previous answers if they exist
        if request.user.is_authenticated:
            user_results = Result.objects.filter(user=request.user, subject=selected_subject)
            user_answers = [(result.question.id, result.selected_answer.id if result.selected_answer else None) for result in user_results]

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

    return render(request, 'user-page.html', {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'questions': questions,
        'remaining_time': remaining_time,
        'user_answers': user_answers,
        'total_questions': total_questions,  # Pass the total number of questions to the template
    })
   
@login_required(login_url='login')
def submit_exam(request):
    subjects = Subject.objects.all()
    results = []

    for subject in subjects:
        exam_sessions = ExamSession.objects.filter(subject=subject)
        questions = [session.question for session in exam_sessions]

        for question in questions:
            session_key = f'answer_{request.user.id}_{subject.id}_{question.id}'
            selected_answer_id = request.session.get(session_key)

            if selected_answer_id:
                selected_answer = question.answers.get(id=selected_answer_id)
                is_correct = selected_answer.is_correct
            else:
                selected_answer = None
                is_correct = False

            # Save or update result to the Result model
            result, created = Result.objects.get_or_create(
                user=request.user,
                subject=subject,
                question=question,
                defaults={
                    'selected_answer': selected_answer,
                    'is_correct': is_correct,
                    'score': 1.0 if is_correct else 0.0
                }
            )

            if not created:
                result.selected_answer = selected_answer
                result.is_correct = is_correct
                result.score = 1.0 if is_correct else 0.0
                result.save()

            results.append({
                'subject': subject,
                'question_id': question.id,
                'selected_answer_id': selected_answer.id if selected_answer else None,
                'correct': is_correct
            })

        # Clear the session answers after submission
        for question in questions:
            session_key = f'answer_{request.user.id}_{subject.id}_{question.id}'
            if session_key in request.session:
                del request.session[session_key]

    # Redirect to the result page with a summary of results per subject
    return redirect(reverse('result'))

def result(request):
    # Get the subjects the user has taken quizzes for
    subjects = Subject.objects.filter(result__user=request.user).distinct()
    subjects_results = {}  # This dictionary will store results per subject

    # Loop through each subject the user has taken the quiz for
    for subject in subjects:
        user_results = []  
        correct_answers = 0
        total_questions = 0

        # Fetch results for this subject
        for result in Result.objects.filter(user=request.user, subject=subject):
            # Get the correct answer for the current question
            correct_answer = result.question.answers.get(is_correct=True)

            # Add the correct answer to the result object
            result.correct_answer = correct_answer
            user_results.append(result)

            # Count the correct answers
            if result.is_correct:
                correct_answers += 1

            total_questions += 1

        subjects_results[subject] = {
            'user_results': user_results,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
        }

    context = {
        'subjects_results': subjects_results,
    }
    return render(request, 'result.html', context)
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
    username = "TIPLOGO CBT CENTRE"
    
    error_message = None

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            user = auth.authenticate(request, username=user_id)
            if user is not None: 
                auth.login(request, user)
                return redirect('welcome')  # Redirect to a succ ess page
            else:
                error_message = "Invalid user ID"
    else:
        form = LoginForm()
        
 
    return render(request, 'login.html', {'form': form, 'error_message': error_message,'username':username})



@login_required(login_url='login')
def index(request):
    user = get_object_or_404(Userprofile ,user=request.user)
    subjects = Subject.objects.all()
    selected_subject_id = request.GET.get('subject_id')
    questions = []
    remaining_time = None
    selected_subject = None
    user_answers = []
    total_questions = 0

    request.session['selected_subject_id'] = selected_subject_id

    if subjects.exists():
        if selected_subject_id:
            selected_subject = Subject.objects.get(id=selected_subject_id)
        else:
            selected_subject = subjects.first()

        # Fetch ExamSession related to the selected subject and shuffle the questions
        exam_sessions = ExamSession.objects.filter(subject=selected_subject).order_by('shuffle_order')
        questions = [session.question for session in exam_sessions]

        # Count the total number of questions
        total_questions = len(questions)

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
            return redirect('login')

        # Retrieve user's previous answers if they exist
        if request.user.is_authenticated:
            user_results = Result.objects.filter(user=request.user, subject=selected_subject)
            user_answers = [(result.question.id, result.selected_answer.id if result.selected_answer else None) for result in user_results]

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
        'user_answers': user_answers,
        'total_questions': total_questions,
        'user':user  
    })
   
 
def welcome(request):
    userprofile = get_object_or_404(Userprofile,user=request.user)
    context = {
        'userprofile':userprofile
    }
    return render (request, 'welcome.html',context) 