from django.shortcuts import render,redirect ,get_object_or_404
from base.models import User ,Userprofile
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='admins:login')
def dashboard(request):
    userprofile = get_object_or_404(Userprofile,user=request.user)
    userid = UserID.objects.count()
    subject = Subject.objects.count()
    qusetion = Question.objects.count()
    context = {
        'userprofile':userprofile,
        'userid':userid,
        'subject':subject,
        'qusetion':qusetion
    }
    return render (request, 'admins/dashboard.html',context)

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        school_name =request.POST.get('school_name')
        username =request.POST.get('username')
        password = request.POST.get('password')
        password1 =request.POST.get('password1')
        
        if password == password1:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'username alrealdy exist')
                return redirect('admins:signup')
            else:
               User.objects.create_user(first_name=first_name,last_name=last_name ,username=username,school_name=school_name,password=password)
               return redirect('admins:login')
            

        else:
            messages.error(request, 'password do not match')
            return redirect('admins:signup')
               

    return render (request, 'admins/create-account.html')

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

def userid(request):
    error_message = None

    if request.method == "POST":
        username= request.POST.get('username')
        last_name = request.POST.get('last_name')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'this Userid has already been generated before, plesase try another name')
            return redirect("admins:userid") 
        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(username=username, last_name=last_name)
                if created:
                    user.set_password(User.objects.make_random_password())
                    user.save()

                unique_id = generate_random_id()
                while UserID.objects.filter(generated_id=unique_id).exists():
                    unique_id = generate_random_id()

                user_id, created = UserID.objects.get_or_create(user=user)
                user_id.generated_id = unique_id
                user_id.save()

                return redirect('admins:user')

        except IntegrityError:
            error_message = "There was an error creating the user. Please try again."  
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
    else:
        userprofile = get_object_or_404(Userprofile,user=request.user)
        context = {
            'userprofile':userprofile,
            'error_message':error_message
        }

    return render(request, 'admins/userid.html',context)  

# views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from docx import Document
from io import BytesIO
import os
import time
from  base.forms import BulkUploadForm
from base.models import Question, Answer ,Subject
  
from django.shortcuts import render, redirect
from django.contrib import messages

from docx import Document
from io import BytesIO
from PIL import Image
import os
import time

@login_required(login_url='login')
def upload(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            subject_text = form.cleaned_data['subject']
            file = request.FILES['file']

            if not file.name.endswith('.docx'):
                messages.error(request, 'Please upload a DOCX file.')
                return redirect('admins:upload')

            try:
                document = Document(file)
                subject, created = Subject.objects.get_or_create(name=subject_text)
                questions_data = parse_document(document)
                
                with transaction.atomic():
                    for question_data in questions_data:
                        save_question_and_answers(
                            question_text=question_data['question_text'],
                            options=question_data['options'],
                            correct_option=question_data['correct_option'],
                            diagram_image_path=question_data['diagram_image_path'],
                            subject=subject
                        )

                messages.success(request, "Questions and answers uploaded successfully!")
                return redirect('admins:question')

            except Exception as e:
                messages.error(request, f"Error processing the file: {e}")
                return redirect('admins:upload')

    else:
        userprofile = get_object_or_404(Userprofile, user=request.user)
        form = BulkUploadForm()

    return render(request, 'admins/upload.html', {'form': form, 'userprofile': userprofile})

def parse_document(document):
    questions_data = []
    question_text = None
    options = []
    correct_option = None
    diagram_image_path = None

    for para in document.paragraphs:
        text = para.text.strip()

        if text.startswith("Q:"):
            if question_text:
                questions_data.append({
                    'question_text': question_text,
                    'options': options,
                    'correct_option': correct_option,
                    'diagram_image_path': diagram_image_path
                })
                options = []
                diagram_image_path = None  # Reset diagram for the next question

            question_text = text.replace("Q:", "").strip()

        elif text.startswith("Correct:"):
            correct_option = text.replace("Correct:", "").strip()

        elif text.startswith(("A.", "B.", "C.", "D.")):
            options.append(text.strip())

        elif text.startswith("DA:"):
            diagram_image_path = extract_and_save_diagram(document)  # Extract a new diagram for the current question

    # Add the last question if any
    if question_text:
        questions_data.append({
            'question_text': question_text,
            'options': options,
            'correct_option': correct_option,
            'diagram_image_path': diagram_image_path
        })

    return questions_data

def save_question_and_answers(question_text, options, correct_option, diagram_image_path, subject):
    question, created = Question.objects.get_or_create(text=question_text, subject=subject)

    if diagram_image_path:
        question.diagram = diagram_image_path
        question.save()

    for option_text in options:
        is_correct = option_text.startswith(correct_option)
        Answer.objects.create(question=question, text=option_text, is_correct=is_correct)

def extract_and_save_diagram(document):
    images = []

    # Extract images from document
    for rel in document.part.rels.values():
        if "image" in rel.target_ref:
            image_stream = BytesIO(rel.target_part.blob)
            image_filename = save_image(image_stream)
            images.append(f'questions/diagrams/{image_filename}')

    for shape in document.inline_shapes:
        if shape.type == 3:  # Shape type 3 means Picture
            image_stream = BytesIO(shape.image.blob)
            image_filename = save_image(image_stream)
            images.append(f'questions/diagrams/{image_filename}')

    return images[0] if images else None

def save_image(image_stream):
    image = Image.open(image_stream)
    image_filename = f'diagram_{int(time.time())}.png'
    image_path = os.path.join('media', 'questions', 'diagrams', image_filename)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)

    # Save the image
    image.save(image_path, format='PNG')

    return image_filename

def user(request):
    userprofile = get_object_or_404(Userprofile,user=request.user)
    
    user_id = UserID.objects.all()
    context = {
        'userprofile':userprofile,   
        "user_id":user_id
    }
    return render(request, 'admins/userget.html',context)

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
from base.models import Suffle,ExamSession , Subject ,Result ,User_result
from django.utils import timezone

import uuid

@login_required(login_url='login')
def launch(request):
    if request.method == 'POST':
        form = MultiSubjectQuestionSelectionForm(request.POST)
        if form.is_valid():
            subject_question_counts = form.cleaned_data['subject_question_counts']
            exam_duration = form.cleaned_data['exam_duration']  # Format hh:mm:ss

            # Loop through selected subjects and their respective number of questions
            for subject, number_of_questions in subject_question_counts.items():
                # Fetch the questions for the subject and shuffle them
                questions = list(Question.objects.filter(subject=subject))
                if len(questions) < number_of_questions:
                    messages.error(request, f"Not enough questions for {subject.name}.")
                    return redirect('admins:launch')  # Redirect back to the form if not enough questions

                # Select a random sample of questions based on the requested number
                selected_questions = random.sample(questions, number_of_questions)

                # Generate a unique session ID for each exam session
                session_id = str(uuid.uuid4())

                # Store each question and its order in the ExamSession model
                for index, question in enumerate(selected_questions):
                    ExamSession.objects.create(
                        session_id=session_id,
                        subject=subject,
                        question=question,
                        exam_start_time=timezone.now(),
                        exam_duration=exam_duration,
                        shuffle_order=index + 1  # Adjust to start from 1 instead of 0
                    )

            messages.success(request, 'Exam preferences have been successfully saved.')
            return redirect('admins:launch')  # Redirect to login to start the exam
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        userprofile = get_object_or_404(Userprofile, user=request.user)
        form = MultiSubjectQuestionSelectionForm()


    return render(request, 'admins/launch.html', {'form': form,'userprofile':userprofile})
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
    userprofile = get_object_or_404(Userprofile,user=request.user)
    subject  = Subject.objects.all()[:10]
    context ={
        'subject':subject,
        'userprofile':userprofile
    }
    return render (request, 'admins/question.html',context)

def delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    subject.delete()
    return redirect('admins:question')


def profile(request):
    userprofile = get_object_or_404(Userprofile,user=request.user)
    context ={ 
       
        'userprofile':userprofile
    }
    return render (request, 'admins/profile.html',context)

from django.db.models import Count, Sum
def result(request):
    userprofile = get_object_or_404(Userprofile,user=request.user)
    # Get the subjects the user has taken quizzes for 
    subjects = Subject.objects.all()  # Get all subjects from the database
    subject_results = {}

    # Loop through each subject and get the results
    for subject in subjects:
        users = Result.objects.filter(subject__name=subject.name).values(
            'user__username', 
            'user__last_name',
            'user__userid__generated_id'
        ).annotate(
            total_answers=Count('id'),  # Total number of answers per user for the subject
            correct_answers=Sum('is_correct')  # Sum of correct answers per user for the subject
        ).distinct()

        # Prepare the results for each subject
        results = []
        for user in users:
            total_answers = user['total_answers']
            correct_answers = user['correct_answers']
            score = f"{correct_answers}/{total_answers}"  # Format the score as 'correct/total'
            
            results.append({
                'first_name': user['user__username'],
                'last_name': user['user__last_name'],
                'user_id': user['user__userid__generated_id'],
                'score': score
            })
        
        # Store the results in a dictionary with the subject name as the key
        subject_results[subject.name] = results

    context = {
        'subject_results': subject_results,
        'userprofile':userprofile
    }
    # Loop through each subject the user has taken the quiz for
    # for subject in subjects:
    #     user_results = []  
    #     correct_answers = 0
    #     total_questions = 0 

    #     # Fetch results for this subject
    #     for result in Result.objects.filter(user=request.user, subject=subject):
    #         # Get the correct answer for the current question
    #         correct_answer = result.question.answers.get(is_correct=True)

    #         # Add the correct answer to the result object
    #         result.correct_answer = correct_answer
    #         user_results.append(result)

    #         # Count the correct answers
    #         if result.is_correct:
    #             correct_answers += 1

    #         total_questions += 1

    #     subjects_results[subject] = {
    #         'user_results': user_results,
    #         'correct_answers': correct_answers,
    #         'total_questions': total_questions,
    #     }

    #     # Create a User_result entry
       
    # context = {
    #     'users':users,
    #     'subjects_results': subjects_results,
    #     'userprofile':userprofile,
    # }
    return render(request, 'admins/result.html', context)