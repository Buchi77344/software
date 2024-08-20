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

# Configure logging
@login_required(login_url='login')
def index(request):
    # Retrieve or create a unique session ID for the exam
    session_id = request.session.get('exam_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        request.session['exam_session_id'] = session_id

    # Retrieve or create the exam session
    exam_session = ExamSession.objects.filter(session_id=session_id).first()
    if not exam_session:
        first_exam_session = ExamSession.objects.first()
        if not first_exam_session:
            return redirect('/')  # Redirect to homepage if no exam session is available

        exam_start_time = timezone.now()
        exam_duration = first_exam_session.exam_duration  # Format hh:mm:ss

        ExamSession.objects.create(
            session_id=session_id,
            subject=first_exam_session.subject,
            exam_start_time=exam_start_time,
            exam_duration=exam_duration
        )
        request.session['exam_start_time'] = exam_start_time.isoformat()
        request.session['exam_duration'] = exam_duration
    else:
        exam_start_time = timezone.datetime.fromisoformat(request.session['exam_start_time'])
        exam_duration = request.session.get('exam_duration', '01:00:00')

    # Calculate the elapsed time and the remaining time
    total_seconds = (timezone.now() - exam_start_time).total_seconds()
    hours, minutes, seconds = map(int, exam_duration.split(':'))
    exam_duration_seconds = hours * 3600 + minutes * 60 + seconds
    remaining_time = max(exam_duration_seconds - total_seconds, 0)

    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        subject = get_object_or_404(Subject, id=subject_id)

        # Retrieve or create exam sessions for this subject
        existing_sessions = ExamSession.objects.filter(session_id=session_id, subject=subject)

        if not existing_sessions.exists():
            # Shuffle and store questions if not already stored
            subject_questions = list(Question.objects.filter(subject=subject))
            if len(subject_questions) < 5:  # Adjust the number of questions as needed
                return redirect('/')  # Handle error or redirect if not enough questions are available

            selected_questions = random.sample(subject_questions, 5)  # Adjust the number of questions as needed
            random.shuffle(selected_questions)

            # Store the shuffled questions in the ExamSession model
            for index, question in enumerate(selected_questions):
                ExamSession.objects.create(
                    session_id=session_id,
                    subject=subject,
                    question=question,
                    exam_start_time=exam_start_time,
                    exam_duration=exam_duration,
                    shuffle_order=index
                )

        selected_questions = [session.question for session in existing_sessions]

        return render(request, 'index.html', {
            'questions': selected_questions,
            'subject': subject,
            'subjects': Subject.objects.all(),  # For navigation bar
            'remaining_time': remaining_time,  # Pass remaining time to the template
        })

    return render(request, 'index.html', {
        'subjects': Subject.objects.all(),  # For navigation bar
        'remaining_time': remaining_time,  # Pass remaining time to the template
    })
# def get_next_subject(current_subject_id):
#     subjects = Subject.objects.all()
#     next_subject = subjects.filter(id__gt=current_subject_id).first()
#     return next_subject
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




def userpage(request):
    return render(request, 'user-page.html')