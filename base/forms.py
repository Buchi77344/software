from django import forms
from base.models import Subject ,Question
class BulkUploadForm(forms.Form):
    subject = forms.CharField(max_length=255, required=True, label='Subject')
    file = forms.FileField(required=True, label='DOCX File')


class SearchForm(forms.Form):
    query = forms.CharField(max_length=500)


class UsernameForm(forms.Form):
    username = forms.CharField(max_length=150)


class LoginForm(forms.Form):
    user_id = forms.CharField(max_length=100, label="User ID")



class MultiSubjectQuestionSelectionForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Select Subjects'
        
    )
    exam_duration = forms.CharField(
        max_length=8,
        initial='01:00:00',
        label='Exam Duration (hh:mm:ss)',
        help_text='Set the duration for the exam in hours, minutes, and seconds.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add a number_of_questions field for each subject
        for subject in Subject.objects.all():
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

        if not self.is_valid_duration(exam_duration):
            self.add_error('exam_duration', 'Please specify a valid exam duration in hh:mm:ss format.')

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

    def is_valid_duration(self, duration):
        try:
            hours, minutes, seconds = map(int, duration.split(':'))
            return (0 <= hours <= 99) and (0 <= minutes < 60) and (0 <= seconds < 60)
        except ValueError:
            return False