from django.shortcuts import render,redirect ,get_object_or_404
from base.models import User ,Userprofile
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='admins:login')
def dashboard(request):
    school_name =get_object_or_404(Name_School)
    userprofile = get_object_or_404(Userprofile,user=request.user)
    userid = UserID.objects.count()
    subject = Subject.objects.count()
    qusetion = Question.objects.count()
    context = {
        'school_name':school_name,
        'userprofile':userprofile,
        'userid':userid,
        'subject':subject,
        'qusetion':qusetion,
    }
    return render (request, 'admins/dashboard.html',context)
from django.contrib.auth import get_user_model
User = get_user_model()

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        school_name = request.POST.get('school_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        is_staff = request.POST.get('is_staff')  # This should be checked if it’s a staff signup
        
        # Check if any admin account already exists
        if is_staff and User.objects.filter(is_staff=True).exists():
            messages.error(request, 'An admin account already exists. You cannot create another one.')
            return redirect('admins:signup')

        if password == password1:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('admins:signup')
            else:
                # Create the user account (setting is_staff=True explicitly for admin creation)
                User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    school_name=school_name,
                    password=password,
                    is_staff=True  # This ensures the created user is an admin
                )
                return redirect('admins:login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('admins:signup')

    return render(request, 'admins/create-account.html')

def login(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = auth.authenticate( username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('admins:dashboard')
        else:         
            messages.error(request, 'Invalid username or password.')
    return render(request, 'admins/login.html')



def forget(request):
    if request.method == "POST":
        recovery_code = request.POST.get('recovery_code')



import random
import string
from django.shortcuts import render
from base.models import User
from base.models import UserID
from  base.forms import UsernameForm
from django.db import IntegrityError, transaction

def generate_random_id():
    numbers = ''.join(random.choice(string.digits) for _ in range(4))
    alphabets = ''.join(random.choice(string.ascii_letters) for _ in range(2))
    random_id = numbers + alphabets
    return ''.join(random.sample(random_id, len(random_id)))
 # Assuming you have this utility function
@login_required(login_url='admins:login')
def userid(request):
    error_message = None
    userprofile = get_object_or_404(Userprofile, user=request.user)
    
    if request.method == "POST": 
        username = request.POST.get('username')
        last_name = request.POST.get('last_name')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'This UserID has already been generated before, please try another name.')
            return redirect("admins:userid") 
        
        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(username=username, last_name=last_name)
                if created:
                    user.set_password(User.objects.make_random_password())
                    user.save()

                unique_id = generate_random_id().upper()
                # Case-insensitive check for existing generated_id
                while UserID.objects.filter(generated_id__iexact=unique_id).exists():
                    unique_id = generate_random_id().upper()

                user_id, created = UserID.objects.get_or_create(user=user)
                user_id.generated_id = unique_id
                user_id.save()

                return redirect('admins:user')

        except IntegrityError:
            error_message = "There was an error creating the user. Please try again."  
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
    
    else:
        school_name = get_object_or_404(Name_School)
        context = {
            'school_name': school_name,
            'error_message': error_message,
            'userprofile': userprofile
        }

    return render(request, 'admins/userid.html', context)  
from django.shortcuts import render, redirect
from django.contrib import messages
from docx import Document
from io import BytesIO
import os
import time
from  base.forms import BulkUploadForm
from base.models import Question, Answer ,Subject ,TermOrSemester, ClassOrLevel
  
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from docx import Document
from io import BytesIO
from PIL import Image
import os
import time
import docx
import re

@login_required(login_url='admins:login')
def upload(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            term_or_semester_value = form.cleaned_data['term_semester']
            class_or_level_value = form.cleaned_data['class_or_level']

            class_or_level, _ = ClassOrLevel.objects.get_or_create(name=class_or_level_value)
            term_or_semester, _ = TermOrSemester.objects.get_or_create(name=term_or_semester_value, class_or_level=class_or_level)

            subjects = form.cleaned_data['subjects'].splitlines()
            files = request.FILES.getlist('files')

            if len(subjects) != len(files):
                messages.error(request, 'The number of subjects must match the number of files.')
                return redirect('admins:upload')

            for subject_text, file in zip(subjects, files):
                if not file.name.endswith('.docx'):
                    messages.error(request, 'Please upload a DOCX file.')
                    return redirect('admins:upload')

                try:
                    document = Document(file)
                    subject, _ = Subject.objects.get_or_create(name=subject_text, term_or_semester=term_or_semester)

                    questions_data = parse_docx(document)

                    if not questions_data:
                        messages.error(request, f"No valid questions found in {file.name}. Please ensure your document is properly formatted.")
                        continue

                    with transaction.atomic():
                        for question_data in questions_data:
                            save_question_and_answers(
                                question_text=question_data['question_text'],
                                options=question_data['options'],
                                correct_option=question_data['correct_option'],
                                subject=subject,
                                term_or_semester=term_or_semester,
                                class_or_level=class_or_level
                            )

                    messages.success(request, f"Questions from {file.name} uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Error processing the file {file.name}: {e}")
                    return redirect('admins:upload')

            return redirect('admins:question')

    else:
        form = BulkUploadForm()

    return render(request, 'admins/upload.html', {'form': form})

def parse_docx(document):
    questions_data = []
    question_block = []
    for para in document.paragraphs:
        line = para.text.strip()
        if line:
            question_block.append(line)
        elif question_block:
            question_data = parse_question_block(question_block)
            if question_data:
                questions_data.append(question_data)
            question_block = []

    if question_block:
        question_data = parse_question_block(question_block)
        if question_data:
            questions_data.append(question_data)

    return questions_data

def parse_question_block(block):
    question_text = ""
    options = []
    correct_option = None

    question_regex = re.compile(r"^\d+\.\s")
    option_regex = re.compile(r"^[A-D]\.\s")
    correct_regex = re.compile(r"^Correct:\s")

    in_question = False

    for line in block:
        line = line.strip()

        if question_regex.match(line):
            if in_question:
                # Finalize the previous question
                if question_text:
                    question_text = re.sub(r"^\d+\.\s", "", question_text)  # Remove numbering
                    return {
                        'question_text': question_text,
                        'options': options,
                        'correct_option': correct_option,
                    }

            # Start a new question block
            question_text = line
            in_question = True

        elif option_regex.match(line):
            options.append(line)

        elif correct_regex.match(line):
            correct_option = line.split(":")[1].strip()

    if in_question and question_text and options and correct_option:
        question_text = re.sub(r"^\d+\.\s", "", question_text)  # Remove numbering
        return {
            'question_text': question_text,
            'options': options,
            'correct_option': correct_option,
        }

    return None

def save_question_and_answers(question_text, options, correct_option, subject, term_or_semester, class_or_level):
    question = Question.objects.create(
        text=question_text,
        subject=subject,
        term_or_semester=term_or_semester,
        class_or_level=class_or_level
    )

    for option in options:
        is_correct = option.startswith(correct_option)
        Answer.objects.create(
            question=question,
            text=option,
            is_correct=is_correct
        )
def export_user_data_to_pdf(request):
    userprofile = get_object_or_404(Userprofile, user=request.user)
    user_id = UserID.objects.all()[:10]
    
    context = {
        'userprofile': userprofile,
        "user_id": user_id
    }
    
    template_path = 'admins/pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="user_data.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors with the PDF creation')
    return response
@login_required(login_url='admins:login')
def user(request):
    userprofile = get_object_or_404(Userprofile, user=request.user)
    school_name = get_object_or_404(Name_School)
    user_id = UserID.objects.all()
    context = {
        'userprofile': userprofile,   
        "user_id": user_id,
        "school_name":school_name
    }
    return render(request, 'admins/userget.html', context)
def deleteuserid(request):
    UserID.objects.all().delete()
    return redirect('admins:user')

import pandas as pd
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def export_user_data_to_pdf(request):
    userprofile = get_object_or_404(Userprofile, user=request.user)
    user_id = UserID.objects.all()[:10]  # Fetching the first 10 UserID objects
    
    context = {
        'userprofile': userprofile,
        "user_id": user_id
    }
    
    template_path = 'admins/pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="user_data.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    # Generate the PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors with the PDF creation')
    return response
from django.shortcuts import render, redirect
from base.forms import MultiSubjectQuestionSelectionForm
from base.models import Suffle,ExamSession , Subject ,Result ,User_result ,Name_School
from django.utils import timezone

import uuid
@login_required(login_url='admins:login')
def launch(request, pk=None):
    school_name = get_object_or_404(Name_School)

    # Get the selected TermOrSemester
    term_or_semester = get_object_or_404(TermOrSemester, pk=pk) if pk else None

    if request.method == 'POST':
        form = MultiSubjectQuestionSelectionForm(request.POST, term_or_semester=term_or_semester)
        if form.is_valid():
            subject_question_counts = form.cleaned_data['subject_question_counts']
            exam_duration = form.cleaned_data['exam_duration']

            for subject, number_of_questions in subject_question_counts.items():
                questions = list(Question.objects.filter(subject=subject, term_or_semester=term_or_semester).order_by('id'))  # Filter by TermOrSemester
                if len(questions) < number_of_questions:
                    messages.error(request, f"Not enough questions for {subject.name}.")
                    return redirect('admins:launch', term_id=pk)  # Pass term_id in redirect

                selected_questions = questions[:number_of_questions]  # Select first N questions

                for index, question in enumerate(selected_questions):
                    ExamSession.objects.create(
                        subject=subject,
                        question=question,
                        exam_start_time=timezone.now(),  # Set start time
                        exam_duration=exam_duration,  # Duration
                        shuffle_order=index + 1  # Store the original order
                    )

            messages.success(request, 'Exam session has been successfully started.')
            return redirect('admins:status')  # Pass term_id in redirect
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MultiSubjectQuestionSelectionForm(term_or_semester=term_or_semester)

    return render(request, 'admins/launch.html', {'form': form, 'school_name': school_name, 'term_or_semester': term_or_semester})
def logout(request):
    auth.logout(request)
    return redirect('admins:login')

import random
from django.shortcuts import render, get_object_or_404
from django.http import Http404

@login_required(login_url='admins:login')
def question_list(request):
    # Retrieve user profile
    user_profile = get_object_or_404(Userprofile, user=request.user)
    subject = user_profile.subject
    number_of_questions = user_profile.number_of_questions

    if not subject or not number_of_questions:
        # Redirect to launch page if preferences are missing
        return redirect('/')  # Or show an appropriate message

    # Validate number_of_questions
    try:
        number_of_questions = int(number_of_questions)
        if number_of_questions < 1:
            raise ValueError("Number of questions must be at least 1.")
    except (ValueError, TypeError):
        raise Http404("Invalid number of questions.")

    # Fetch all questions for the subject
    subject_questions = Question.objects.filter(subject=subject).prefetch_related('answers')

    # Shuffle questions based on user ID or username if authenticated
    random.seed(request.user.id)  
    subject_questions = list(subject_questions)  # Convert queryset to list for shuffling
    random.shuffle(subject_questions)

    # Limit the number of questions to show
    questions_to_show = subject_questions[:number_of_questions]

    # Render the questions and answers in the template
    return render(request, 'admins/question_list.html', {
        'questions': questions_to_show,
    })

from base.forms import SearchForm 
from django.db.models import Q
def search(request):
    
    form = SearchForm()
    query = None
    result = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            result = UserID.objects.filter(
                Q(generated_id__icontains=query) |
                Q(user__username__icontains=query)|
                Q(user__last_name__icontains=query)
            )
    return render(request, 'admins/search.html', {'form': form, 'query': query, 'result': result})

def question(request):
    school_name =get_object_or_404(Name_School)
    classes = ClassOrLevel.objects.all()
    context ={
        'subject':subject,
        'school_name':school_name,
        'classes':classes,
    }
    return render (request, 'admins/question.html',context)

def delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    subject.delete()
    return redirect('admins:question')


def profile(request):
   
    school_name =get_object_or_404(Name_School)
    if request.method == 'POST':
        school =request.POST.get('school')
        school_name.school = school
        school_name.save()
        return redirect('admins:profile')

    context ={ 
       
       
        'school_name':school_name
    }
    return render (request, 'admins/profile.html',context)

from django.db.models import Count, Sum
from django.db.models import Count, Sum, IntegerField, Case, When

@login_required(login_url='admins:login')
def result(request):
    userprofile = get_object_or_404(Userprofile, user=request.user)
    
    # Retrieve all ClassOrLevel and TermOrSemester
    classes = ClassOrLevel.objects.all()
    term_or_semesters = TermOrSemester.objects.all()

    # Dictionary to store results by subject, class, and term
    subject_results = {}

    for class_or_level in classes:
        for term_or_semester in term_or_semesters.filter(class_or_level=class_or_level):
            subjects = Subject.objects.filter(term_or_semester=term_or_semester)

            for subject in subjects:
                # Get results for the current subject, class, and term
                users = Result.objects.filter(subject=subject).values(
                    'user__username',
                    'user__last_name',
                    'user__userid__generated_id'
                ).annotate(
                    total_answers=Count('id'),
                    correct_answers=Sum(
                        Case(
                            When(is_correct=True, then=1),
                            When(is_correct=False, then=0),
                            output_field=IntegerField()
                        )
                    )
                ).distinct()

                results = []
                for user in users:
                    total_answers = user['total_answers']
                    correct_answers = user['correct_answers']
                    score = f"{correct_answers}/{total_answers}"

                    results.append({
                        'first_name': user['user__username'],
                        'last_name': user['user__last_name'],
                        'user_id': user['user__userid__generated_id'],
                        'score': score
                    })

                subject_results[(class_or_level.name, term_or_semester.name, subject.name)] = results

    context = {
        'subject_results': subject_results,
        'userprofile': userprofile
    }

    return render(request, 'admins/result.html', context)
@login_required(login_url='admins:login')
def term (request,pk):
    class_or_level = get_object_or_404(ClassOrLevel, pk=pk)
    terms = TermOrSemester.objects.filter(class_or_level=class_or_level)
    context = {
        'terms':terms
    }
    return render (request, 'admins/term.html',context)
@login_required(login_url='admins:login')
def subject(request,pk):
    term_or_semester = get_object_or_404(TermOrSemester, pk=pk)
    subjects = Subject.objects.filter(term_or_semester=term_or_semester)
    context = {
        'subjects':subjects
    }
    return render (request, 'admins/subject.html',context) 

def status(request):
   
    return render (request, 'admins/status.html') 

def destroyexam(request):
    ExamSession.objects.all().delete()
    return redirect('admins:question')

def releaseip(request):
    userid = UserID.objects.all()

    context = {
        'userid':userid,
    }
    return render (request, 'admins/releaseip.html',context)


def ip(request, user):
    user_instance = get_object_or_404(User, username=user)
    user_instance.session_id = None
    user_instance.save()
    messages.success(request, 'IP address has been successfully released.')
    return redirect('admins:releaseip')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json

@csrf_exempt
def close_tab(request):
  session_id =  request.user.session_id
  if User.objects.filter(session_id =session_id ,user=request.user).exists:
    return JsonResponse({'session_exists': True})
    
        
  else:
        return JsonResponse({'session_exists': False})


def user_status_api(request):
    user_statuses = UserID.objects.select_related('user').values('id', 'user__is_online')
    return JsonResponse(list(user_statuses), safe=False)