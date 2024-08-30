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
from datetime import timedelta

@login_required(login_url='login')
@login_required(login_url='login')
def userpage(request):
    subjects = Subject.objects.all()
    selected_subject_id = request.GET.get('subject_id')
    questions = []
    remaining_time = None
    selected_subject = None
    user_answers = []
    total_questions = 0

    if subjects.exists():
        if selected_subject_id:
            selected_subject = get_object_or_404(Subject, id=selected_subject_id)
        else:
            selected_subject = subjects.first()

        # Check if an exam session already exists for this user and subject
        session_id = f'{request.user.id}_{selected_subject.id}'
        exam_sessions = ExamSession.objects.filter(session_id=session_id, subject=selected_subject)

        if not exam_sessions.exists():
            # Create a new exam session with shuffled questions and start time
            questions = list(Question.objects.filter(subject=selected_subject))
            random.shuffle(questions)
            start_time = timezone.now()
            duration = '01:00:00'  # Example duration of 1 hour

            for index, question in enumerate(questions):
                ExamSession.objects.create(
                    session_id=session_id,
                    subject=selected_subject,
                    question=question,
                    exam_start_time=start_time,
                    exam_duration=duration,
                    shuffle_order=index,
                )

        # Fetch the user's exam session
        exam_sessions = ExamSession.objects.filter(session_id=session_id, subject=selected_subject).order_by('shuffle_order')
        questions = [session.question for session in exam_sessions]
        total_questions = len(questions)

        # Calculate remaining time based on the user's start time
        if exam_sessions.exists():
            start_time = exam_sessions.first().exam_start_time
            duration_parts = exam_sessions.first().exam_duration.split(':')
            duration = timedelta(hours=int(duration_parts[0]), minutes=int(duration_parts[1]), seconds=int(duration_parts[2]))
            end_time = start_time + duration
            remaining_time = max(0, (end_time - timezone.now()).total_seconds())

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

            # Mark the exam as completed
            ExamSession.objects.filter(session_id=session_id, subject=selected_subject).update(completed=True)

            # Redirect to the result page
            return redirect('login')

        # Retrieve user's previous answers if they exist
        if request.user.is_authenticated:
            user_results = Result.objects.filter(user=request.user, subject=selected_subject)
            user_answers = [(result.question.id, result.selected_answer.id if result.selected_answer else None) for result in user_results]

    return render(request, 'user-page.html', {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'questions': questions,
        'remaining_time': remaining_time,
        'user_answers': user_answers,
        'total_questions': total_questions,
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
from .models import Question, Answer ,Result ,Name_School,UserExamSessionx









import random
import string
from django.shortcuts import render
from .models import User
from .models import UserID ,Loding
from .forms import UsernameForm
from django.db import IntegrityError, transaction

def generate_random_id(length=6):
    characters = string.ascii_lowercase + string.digits
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


from django.shortcuts import render, redirect
from django.contrib import auth
from .forms import LoginForm

def login(request):
    
    username = get_object_or_404(Name_School)
    
    error_message = None

    if request.method == "POST":
        form = LoginForm(request.POST)
      
        if form.is_valid(): 
            user_id = form.cleaned_data['user_id']
            user_id = ''.join([char.upper() if char.isalpha() else char for char in user_id])
           
            user = auth.authenticate(request, username=user_id)
            if user is not None: 
               if Loding.objects.filter(login=True ,user =request.user).exists():
                 messages.error(request, 'you can not login again')
                 return redirect('login')
               auth.login(request, user)
               return redirect('welcome')  
            else:
                error_message = "Invalid user ID"  
    else: 
        form = LoginForm()
        
 
    return render(request, 'login.html', {'form': form, 'error_message': error_message,'username':username})



from collections import defaultdict

@login_required(login_url='login')
def index(request):
    username = get_object_or_404(UserID, user=request.user)
    school_name = get_object_or_404(Name_School)
    subjects = Subject.objects.all()

    all_subjects_questions = []
    remaining_time = None
    user_answers = defaultdict(dict)

    if subjects.exists():
        for subject in subjects:
            exam_sessions = ExamSession.objects.filter(subject=subject).order_by('shuffle_order')
            questions = [session.question for session in exam_sessions]

            # Shuffle questions uniquely for each user and subject
            seed = hash(request.user.id) % 10000
            random.seed(seed)
            random.shuffle(questions)

            all_subjects_questions.append({
                'subject': subject,
                'questions': questions
            })

            if exam_sessions.exists():
                exam_session = exam_sessions.first()

                user_exam_session, created = UserExamSessionx.objects.get_or_create(
                    user=request.user,
                    subject=subject,
                    defaults={'exam_session': exam_session, 'start_time': timezone.now()}
                )

                duration_parts = exam_session.exam_duration.split(':')
                duration = timedelta(hours=int(duration_parts[0]), minutes=int(duration_parts[1]), seconds=int(duration_parts[2]))
                end_time = user_exam_session.start_time + duration

                remaining_time = max(0, (end_time - timezone.now()).total_seconds())

            if request.user.is_authenticated:
                user_results = Result.objects.filter(user=request.user, subject=subject)
                for result in user_results:
                    user_answers[question.id] = result.selected_answer.id if result.selected_answer else None

    if request.method == 'POST':
        for subject_data in all_subjects_questions:
            subject = subject_data['subject']
            questions = subject_data['questions']
            for question in questions:
                selected_answer_id = request.POST.get(f'question_{question.id}')
                if selected_answer_id:
                    selected_answer = question.answers.get(id=selected_answer_id)
                    is_correct = selected_answer.is_correct
                else:
                    selected_answer = None
                    is_correct = False

                Result.objects.create(
                    user=request.user,
                    subject=subject,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=is_correct,
                    score=1.0 if is_correct else 0.0
                   
                )
                los , created=Loding.objects.update_or_create(login=True ,user =request.user)
                los.save()
               
                  
                return redirect('complete')
    
    return render(request, 'index.html', {
        'subjects': subjects,
        'all_subjects_questions': all_subjects_questions,
        'remaining_time': remaining_time,
        'user_answers': user_answers,
        'school_name': school_name,
        'username': username
    })
def welcome(request):
    userprofile = get_object_or_404(Userprofile,user=request.user)
    context = {
        'userprofile':userprofile
    }
    return render (request, 'welcome.html',context) 

@login_required(login_url='login')
def complete(request):
    return render(request, 'exam_complete.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserSelection
import json

@csrf_exempt
def save_selection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')

        if request.user.is_authenticated:  # Ensure the user is logged in
            selection, created = UserSelection.objects.update_or_create(
                user=request.user,
                question_id=question_id,
                defaults={'selected_answer_id': answer_id},
            )
            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)

def get_selections(request):
    if request.user.is_authenticated:
        user_selections = UserSelection.objects.filter(user=request.user)
        selected_answers = {selection.question_id: selection.selected_answer_id for selection in user_selections}
        return JsonResponse({'selected_answers': selected_answers})

    return JsonResponse({'status': 'failed'}, status=400)
from django.views.decorators.http import require_POST
def submit_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subject_id = data.get('subject_id')
        question_id = data.get('question_id')
        selected_answer_id = data.get('selected_answer_id')

        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'No Subject matches the given query.'})

        try:
            question = Question.objects.get(id=question_id, subject=subject)
        except Question.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'No Question matches the given query.'})

        try:
            selected_answer = Answer.objects.get(id=selected_answer_id, question=question)
        except Answer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'No Answer matches the given query.'})

        # Further processing here...
        # Check if the selected answer is correct
        is_correct = selected_answer.is_correct
        score = 1.0 if is_correct else 0.0

        # Save the result to the database
        Result.objects.update_or_create(
            user=request.user,
            subject=subject,
            question=question,
            defaults={
                'selected_answer': selected_answer,
                'is_correct': is_correct,
                'score': score
            }
        )

        return JsonResponse({'status': 'success', 'message': 'Answer submitted successfully!'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})