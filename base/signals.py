# yourapp/signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

@receiver(user_logged_in)
def set_exam_start_time(sender, request, user, **kwargs):
    if 'exam_start_time' not in request.session:
        request.session['exam_start_time'] = timezone.now().isoformat()
        request.session['exam_time_limit'] = 60  # Default to 60 minutes if not set
