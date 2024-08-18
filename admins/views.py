from django.shortcuts import render,redirect ,get_object_or_404
from base.models import User ,Userprofile
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='admins:login')
def dashboard(request):
    userprofile = get_object_or_404(Userprofile,user=request.user)
    context = {
        'userprofile':userprofile
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

def generate_random_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

 # Assuming you have this utility function

def userid(request):
    error_message = None

    if request.method == "POST":
        username= request.POST.get('username')
        last_name = request.POST.get('last_name')

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

def upload(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            subject_text = form.cleaned_data['subject']
            file = request.FILES['file']

            try:
                if not file.name.endswith('.docx'):
                    messages.error(request, 'Please upload a DOCX file.')
                    return redirect('admins:upload')

                document = Document(file)
                question_text = None
                options = []
                correct_option = None
                diagram_image_path = None

                subject, created = Subject.objects.get_or_create(name=subject_text)

                for para in document.paragraphs:
                    text = para.text.strip()

                    if text.startswith("Q:"):
                        if question_text:
                            save_question_and_answers(question_text, options, correct_option, diagram_image_path, subject)
                            options = []
                            diagram_image_path = None  # Clear the diagram after saving the question

                        question_text = text.replace("Q:", "").strip()

                    elif text.startswith("Correct:"):
                        correct_option = text.replace("Correct:", "").strip()

                    elif text.startswith("A.") or text.startswith("B.") or text.startswith("C.") or text.startswith("D."):
                        options.append(text.strip())

                    elif text.startswith("DA:"):
                        diagram_image_path = extract_and_save_diagram(document)  # Extract a new diagram for the current question

                if question_text:
                    save_question_and_answers(question_text, options, correct_option, diagram_image_path, subject)

                messages.success(request, "Questions and answers uploaded successfully!")
                return redirect('/')

            except Exception as e:
                messages.error(request, f"Error processing the file: {e}")
                return redirect('admins:upload')

    else:
        form = BulkUploadForm()

    return render(request, 'admins/upload.html', {'form': form})

def save_question_and_answers(question_text, options, correct_option, diagram_image_path, subject):
    question, created = Question.objects.get_or_create(text=question_text, subject=subject)

    if diagram_image_path:
        question.diagram = diagram_image_path
        question.save()

    for option_text in options:
        is_correct = (option_text.startswith(correct_option))
        Answer.objects.create(question=question, text=option_text, is_correct=is_correct)

def extract_and_save_diagram(document):
    images = []

    # Extract images from document
    for rel in document.part.rels.values():
        if "image" in rel.target_ref:
            image_stream = BytesIO(rel.target_part.blob)
            image_filename = save_image(image_stream)
            images.append(f'questions/diagrams/{image_filename}')

    # If no images found, attempt to extract shapes (they might be stored as images)
    # Note: Shapes extraction is complex and may need manual adjustments
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
    user_id = UserID.objects.all()
    context = {
        "user_id":user_id
    }
    return render(request, 'admins/userget.html',context)
def launch(request):
    return render(request, 'admins/launch.html')

def logout(request):
    auth.logout(request)
    return redirect('admins:login')

def question_list(request):
    # Fetch all questions
    questions = list(Question.objects.all().select_related('subject').prefetch_related('answers'))

    # Use the user's ID or username to seed the random shuffle
    if request.user.is_authenticated:
        random.seed(request.user.id)  # or use request.user.username

    random.shuffle(questions)

    return render(request, 'admins/question_list.html', {'questions': questions})