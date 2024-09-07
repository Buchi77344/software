# from django.shortcuts import redirect
# from django.core.cache import cache
# from django.urls import reverse
# from django.utils.timezone import now
# from django.conf import settings

# class RootRedirectMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Get the current path
#         path = request.path_info
        
#         # Check if the request is for the root URL
#         if path == '/':
#             # Check if the user is authenticated
#             if not request.user.is_authenticated:
#                 # Redirect to the base login URL
#                 login_url = reverse('login')
#                 return redirect(login_url)
            
#             # Check if the user is accessing the root URL within 20 seconds
#             last_access = cache.get(f'user_last_access_{request.user.id}')
#             current_time = now()
#             if last_access:
#                 time_diff = (current_time - last_access).total_seconds()
#                 if time_diff < 600:
#                     # Redirect to login page if accessed again within 20 seconds
#                     login_url = reverse('login')
#                     return redirect(login_url)
            
#             # Update last access time in cache
#             cache.set(f'user_last_access_{request.user.id}', current_time, timeout=None)

#         # Proceed with normal request processing
#         response = self.get_response(request)
#         return response
