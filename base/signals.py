# from django.contrib.auth.signals import user_logged_in, user_logged_out
# from django.dispatch import receiver
# from .models import UserExamSessionx

# @receiver(user_logged_out)
# def pause_exam_on_logout(sender, request, user, **kwargs):
#     try:
#         user_exam_sessions = UserExamSessionx.objects.filter(user=user, paused_time=False)
#         for session in user_exam_sessions:
#             session.pause()
#     except UserExamSessionx.DoesNotExist:
#         pass

# @receiver(user_logged_in)
# def resume_exam_on_login(sender, request, user, **kwargs):
#     try:
#         user_exam_sessions = UserExamSessionx.objects.filter(user=user, paused_time=True)
#         for session in user_exam_sessions:
#             session.resume()
#     except UserExamSessionx.DoesNotExist:
#         pass
