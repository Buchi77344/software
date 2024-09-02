from django import forms
from base.models import Subject ,Question
from django.forms.widgets import ClearableFileInput

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if isinstance(files.get(name), list):
            return files.getlist(name)
        return files.get(name)


TERM_CHOICES = [
    ('First Term', 'First Term'),
    ('Second Term', 'Second Term'),
    ('Third Term', 'Third Term'),
]

SEMESTER_CHOICES = [
    ('first semester', 'First Semester'),
    ('second semester', 'Second Semester'),
]
GENERAL  = [
    ('general exam', 'General Exam'),
]
TERM_SEMESTER_CHOICES = TERM_CHOICES + SEMESTER_CHOICES + GENERAL 

CLASS_LEVEL_CHOICES = [
    ('jss1', 'JSS 1'),
    ('jss2', 'JSS 2'),
    ('jss3', 'JSS 3'),
    ('sss1', 'SSS 1'),
    ('sss2', 'SSS 2'),
    ('sss3', 'SSS 3'),
    ('cbt', 'CBT'),
    ('level 100', 'Level 100'),
    ('level 200', 'Level 200'),
    ('level 300', 'Level 300'),
    ('level 400', 'Level 400'),
]

class BulkUploadForm(forms.Form):
    term_semester = forms.ChoiceField(choices=TERM_SEMESTER_CHOICES, required=True, label='Term/Semester')
    class_or_level = forms.ChoiceField(choices=CLASS_LEVEL_CHOICES, required=True, label='Class/Level')
    subjects = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.Textarea(attrs={'rows': 10}),
        label='Subjects (One per line, corresponding to each file)'
    )
    files = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}),
        required=True,
        label='DOCX Files (Attach files in the same order as subjects)'
    )
class SearchForm(forms.Form):
    query = forms.CharField(max_length=500)


class UsernameForm(forms.Form):
    username = forms.CharField(max_length=150)


class LoginForm(forms.Form):
    user_id = forms.CharField(max_length=100, label="User ID")



class MultiSubjectQuestionSelectionForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),  # Start with an empty queryset
        widget=forms.CheckboxSelectMultiple,
        label='Select Subjects'
    )
    
    # Generate 15-minute interval choices from 15 minutes to 4 hours
    DURATION_CHOICES = [
        (f"{h:02}:{m:02}:00", f"{h}h {m}m") 
        for h in range(4) for m in (0, 15, 30, 45)
    ] + [("04:00:00", "4h 00m")]

    exam_duration = forms.ChoiceField(
        choices=DURATION_CHOICES,
        initial='01:00:00',
        label='Exam Duration',
        help_text='Select the duration for the exam.'
    )

    def __init__(self, *args, **kwargs):
        term_or_semester = kwargs.pop('term_or_semester', None)  # Get the term_or_semester argument
        super().__init__(*args, **kwargs)
        
        # Filter the subjects based on the selected term_or_semester
        if term_or_semester:
            self.fields['subjects'].queryset = Subject.objects.filter(term_or_semester=term_or_semester)
        
        # Dynamically add a number_of_questions field for each filtered subject
        for subject in self.fields['subjects'].queryset:
            self.fields[f'number_of_questions_{subject.id}'] = forms.IntegerField(
                min_value=1,
                label=f'Number of Questions for {subject.name}',
                required=False
            )

    def clean(self):
        cleaned_data = super().clean()
        subjects = cleaned_data.get('subjects')
        exam_duration = cleaned_data.get('exam_duration')
        subject_question_counts = {}

        if not subjects:
            self.add_error('subjects', 'At least one subject must be selected.')

        if exam_duration not in dict(self.DURATION_CHOICES).keys():
            self.add_error('exam_duration', 'Please select a valid exam duration.')

        for subject in subjects:
            number_of_questions = cleaned_data.get(f'number_of_questions_{subject.id}')
            if number_of_questions is None:
                self.add_error(f'number_of_questions_{subject.id}', f'Please specify the number of questions for {subject.name}.')
            else:
                available_questions = Question.objects.filter(subject=subject).count()
                if number_of_questions > available_questions:
                    self.add_error(f'number_of_questions_{subject.id}', f'The number of questions for {subject.name} cannot exceed {available_questions}.')
                subject_question_counts[subject] = number_of_questions

        # Store subject_question_counts and duration for later use
        cleaned_data['subject_question_counts'] = subject_question_counts
        cleaned_data['exam_duration'] = exam_duration

        return cleaned_data
