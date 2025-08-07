from .views import RegisterUserView, LoginView, InviteUserView, CustomPasswordResetConfirmView, ListDispatchersView, ListDriversView, DeleteUserView, CreateLoadView, ListLoadsView, ListUnassignedLoadsView, ListAssignedLoadsView, CreateAssignmentView, IndividualChatView, CheckInView, CheckOutView
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

#AssignLoadToDriverView,

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register-user'),

    path('login/', LoginView.as_view(), name='login'),

    path('reset-password/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('invite/', InviteUserView.as_view(), name='invite-user'),

    path('reset-password-done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('users/drivers/', ListDriversView.as_view(), name='list-drivers'),

    path('users/dispatchers/', ListDispatchersView.as_view(), name='list-dispatchers'),

    path('users/delete/<int:user_id>/', DeleteUserView.as_view(), name='delete-user'),

    path('create-load/', CreateLoadView.as_view(), name='create-load'),

    path('list-loads/', ListLoadsView.as_view(), name='list-loads'),

    # path('assign-load/<int:load_id>/', AssignLoadToDriverView.as_view(), name='assign-load'),
    path('unassigned-loads/', ListUnassignedLoadsView.as_view(), name='list-unassigned-loads'),

    path('assigned-loads/', ListAssignedLoadsView.as_view(), name='list-assigned-loads'),

    path('create-assignment/', CreateAssignmentView.as_view(), name='create-assignment'),

    path('update-assignment/<int:assignment_id>/', CreateAssignmentView.as_view(), name='update-assignment'),

    path('chatroom/', views.chatroom, name='chatroom'),

    path('messages/<int:target_user_id>/', IndividualChatView.as_view(), name='individual_chat'),

    path('check-in/', CheckInView.as_view(), name='check_in'),
    path('check-out/', CheckOutView.as_view(), name='check_out'),

]

