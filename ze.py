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
                cleaned_document = clean_document(document)
                subject, created = Subject.objects.get_or_create(name=subject_text)
                questions_data = parse_document(cleaned_document)

                if not questions_data:
                    messages.error(request, "No valid questions found. Please ensure your document is properly formatted.")
                    return redirect('admins:upload')

                with transaction.atomic():
                    for question_data in questions_data:
                        success = save_question_and_answers(
                            question_text=question_data['question_text'],
                            options=question_data['options'],
                            correct_option=question_data['correct_option'],
                            diagram_image_path=question_data['diagram_image_path'],
                            subject=subject
                        )
                        if not success:
                            messages.error(request, f"Failed to save question: {question_data['question_text']}")
                            return redirect('admins:upload')

                messages.success(request, "Questions uploaded successfully!")
                return redirect('admins:question')

            except Exception as e:
                messages.error(request, f"Error processing the file: {e}")
                return redirect('admins:upload')

    else:
        school_name = get_object_or_404(Name_School)
        form = BulkUploadForm()

    return render(request, 'admins/upload.html', {'form': form, 'school_name': school_name})

def clean_document(document):
    cleaned_paragraphs = []
    last_label = None

    for para in document.paragraphs:
        text = para.text.strip()

        if text.startswith(("Q:", "A.", "B.", "C.", "D.", "Correct:", "DA:")):
            last_label = text[:2]
            cleaned_paragraphs.append(text)
        else:
            # Handle missing or incorrect labels by continuing from the last valid label
            if last_label and not text.startswith("Q:"):
                cleaned_paragraphs[-1] += " " + text
            else:
                cleaned_paragraphs.append(text)

    cleaned_document = Document()
    for cleaned_text in cleaned_paragraphs:
        cleaned_document.add_paragraph(cleaned_text)

    return cleaned_document

def parse_document(document):
    questions_data = []
    question_text = None
    options = []
    correct_option = None
    diagram_image_path = None
    expecting_diagram = False

    for para in document.paragraphs:
        text = para.text.strip()

        if text.startswith("Q:"):
            if question_text:
                if all([options, correct_option]):
                    questions_data.append({
                        'question_text': question_text,
                        'options': options,
                        'correct_option': correct_option,
                        'diagram_image_path': diagram_image_path
                    })
                else:
                    # Skip incomplete questions and log the error
                    messages.warning(request, f"Incomplete question ignored: {question_text}")

                options = []
                correct_option = None
                diagram_image_path = None

            question_text = text.replace("Q:", "").strip()

        elif text.startswith("Correct:"):
            correct_option = text.replace("Correct:", "").strip()

        elif text.startswith(("A.", "B.", "C.", "D.")):
            options.append(text.strip())

        elif "DA:" in text:
            expecting_diagram = True
            diagram_image_path = extract_and_save_diagram_or_shape(document, para)

        if expecting_diagram and diagram_image_path is None:
            diagram_image_path = extract_and_save_diagram_or_shape(document, para)
            expecting_diagram = False

    if question_text:
        if all([options, correct_option]):
            questions_data.append({
                'question_text': question_text,
                'options': options,
                'correct_option': correct_option,
                'diagram_image_path': diagram_image_path
            })
        else:
            messages.warning(request, f"Incomplete question ignored: {question_text}")

    return questions_data

def extract_and_save_diagram_or_shape(document, paragraph):
    images = []

    try:
        para_index = document.paragraphs.index(paragraph)
        
        if paragraph._element.xpath('.//pic:pic'):
            images += extract_images_from_paragraph(paragraph)

        if para_index > 0:
            prev_para = document.paragraphs[para_index - 1]
            if prev_para._element.xpath('.//pic:pic'):
                images += extract_images_from_paragraph(prev_para)

        if para_index < len(document.paragraphs) - 1:
            next_para = document.paragraphs[para_index + 1]
            if next_para._element.xpath('.//pic:pic'):
                images += extract_images_from_paragraph(next_para)

    except ValueError:
        pass

    return images[0] if images else None

def extract_images_from_paragraph(paragraph):
    images = []
    for rel in paragraph.part.rels.values():
        if "image" in rel.target_ref:
            image_stream = BytesIO(rel.target_part.blob)
            image_filename = save_image(image_stream)
            if image_filename:
                images.append(f'questions/diagrams/{image_filename}')
    return images

def save_image(image_stream):
    image = Image.open(image_stream)
    image_filename = f'diagram_{int(time.time())}.png'
    image_path = os.path.join('media', 'questions', 'diagrams', image_filename)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)

    try:
        image.save(image_path, format='PNG')
        return image_filename
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def save_question_and_answers(question_text, options, correct_option, diagram_image_path, subject):
    question, created = Question.objects.get_or_create(text=question_text, subject=subject)

    if diagram_image_path:
        question.diagram = diagram_image_path
        question.save()

    for option_text in options:
        is_correct = option_text.startswith(correct_option)
        Answer.objects.create(question=question, text=option_text, is_correct=is_correct)

    return True

def user(request):
    userprofile = get_object_or_404(Userprofile, user=request.user)
    
    user_id = UserID.objects.all()
    context = {
        'userprofile': userprofile,   
        "user_id": user_id
    }
    return render(request, 'admins/userget.html', context)
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