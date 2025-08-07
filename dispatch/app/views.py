from django.shortcuts import render

# Create your views here.


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, DispatcherListSerializer, DriverListSerializer, LoadSerializer, AssignmentSerializer, MessageSerializer, CheckInOutSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from .models import Load, Message, CheckInOut
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Q  # You also need to import Q for filtering
from django.utils import timezone



User = get_user_model()

class RegisterUserView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Check if user is active
            if not user.is_active:
                return Response({"detail": "User is deactivated."}, status=status.HTTP_403_FORBIDDEN)

            # Generate JWT token (access and refresh)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "access_token": access_token,
                "refresh_token": str(refresh),
                "user_type": user.user_type,  # Optional: Send back user type if needed
            }, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

#
# class InviteUserView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         user_type = request.data.get('user_type')  # 'driver' or 'dispatcher'
#
#         # Check if email and user_type are provided
#         if not email or not user_type:
#             return Response({"detail": "Email and user type are required."}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Check if the email already exists
#         if User.objects.filter(email=email).exists():
#             return Response({"detail": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Create the user with status 'inactive' until they set their password
#         user = User.objects.create_user(email=email, password=None, user_type=user_type, is_active=False)
#
#         # Generate a token for the user
#         token = default_token_generator.make_token(user)
#         uid = urlsafe_base64_encode(str(user.pk).encode())
#
#         # Send an email with the password reset link
#         reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
#
#         subject = "Your Invitation to Set Your Password"
#         message = f"Hi {user.email},\n\nPlease click the following link to set your password:\n{reset_link}\n\nRegards,\nYour Company"
#         send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
#
#         return Response({"detail": "Invitation sent to email."}, status=status.HTTP_200_OK)


class InviteUserView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        email = request.data.get('email')
        user_type = request.data.get('user_type')  # 'driver' or 'dispatcher'

        # Check if email and user_type are provided
        if not email or not user_type:
            return Response({"detail": "Email and user type are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            return Response({"detail": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user with status 'inactive' until they set their password
        user = User.create_user(email=email, password=None, user_type=user_type, is_active=False)

        # Generate a token for the user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())

        # Send an email with the password reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        subject = "Your Invitation to Set Your Password"
        message = f"Hi {user.email},\n\nPlease click the following link to set your password:\n{reset_link}\n\nRegards,\nYour Company"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return Response({"detail": "Invitation sent to email."}, status=status.HTTP_200_OK)


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    Custom Password Reset View to update the user's is_active field after password reset.
    """
    # template_name = 'registration/password_reset_confirm'

    def form_valid(self, form):
        # Call the parent class method to set the new password
        user = form.save()

        # Set is_active to True after password reset
        user.is_active = True
        user.save()

        # Redirect the user to a success page after password is reset
        return HttpResponseRedirect(reverse_lazy('password_reset_complete'))

#
# class ListDriversView(APIView):
#     permission_classes = [IsAdminUser]
#
#     def get(self, request):
#         drivers = User.objects.filter(user_type='driver').select_related()
#         serializer = UserListSerializer(drivers, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class ListDriversView(APIView):
    permission_classes = [IsAdminUser]


    def get(self, request):
        # Fetch only drivers
        drivers = User.objects.filter(user_type='driver').select_related()
        serializer = DriverListSerializer(drivers, many=True)  # Use the driver serializer
        return Response(serializer.data, status=status.HTTP_200_OK)

# class ListDispatchersView(APIView):
#     permission_classes = [IsAdminUser]
#
#     def get(self, request):
#         dispatchers = User.objects.filter(user_type='dispatcher').select_related()
#         serializer = UserListSerializer(dispatchers, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class ListDispatchersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Fetch only dispatchers
        dispatchers = User.objects.filter(user_type='dispatcher').select_related()
        serializer = DispatcherListSerializer(dispatchers, many=True)  # Use the dispatcher serializer
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteUserView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id, user_type__in=['driver', 'dispatcher'])
            user.delete()
            return Response({"detail": "User deleted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found or not a driver/dispatcher."}, status=status.HTTP_404_NOT_FOUND)


class CreateLoadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Ensure only admins can create loads
        if request.user.user_type != 'admin':
            return Response({"detail": "You do not have permission to create loads."}, status=status.HTTP_403_FORBIDDEN)

        # Initialize the serializer with the provided data
        serializer = LoadSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Admin creating the load, associate the load with the admin user
            serializer.save(admin_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListLoadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all the loads
        loads = Load.objects.all()

        # Serialize the loads
        serializer = LoadSerializer(loads, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListUnassignedLoadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all the loads with status 'unassigned'
        unassigned_loads = Load.objects.filter(status='unassigned')

        # Serialize the unassigned loads
        serializer = LoadSerializer(unassigned_loads, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)

class ListAssignedLoadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all the loads with status 'assigned'
        assigned_loads = Load.objects.filter(status='assigned')

        # Serialize the assigned loads
        serializer = LoadSerializer(assigned_loads, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListDriversView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all users with user_type 'driver'
        drivers = User.objects.filter(user_type='driver').values('id', 'first_name', 'last_name')

        # Return the list of drivers with only id and name
        return Response(drivers, status=status.HTTP_200_OK)


#
# class AssignLoadToDriverView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, load_id):
#         # Check if the user is admin or dispatcher
#         if request.user.user_type not in ['admin', 'dispatcher']:
#             return Response({"detail": "You do not have permission to assign loads."}, status=status.HTTP_403_FORBIDDEN)
#
#         try:
#             load = Load.objects.get(id=load_id)
#         except Load.DoesNotExist:
#             return Response({"detail": "Load not found."}, status=status.HTTP_404_NOT_FOUND)
#
#         # Check if the user is the dispatcher who created the load
#         if load.dispatcher != request.user and request.user.user_type != 'admin':
#             return Response({"detail": "You can only assign loads you have created."}, status=status.HTTP_403_FORBIDDEN)
#
#         driver_id = request.data.get('driver_id')
#         if not driver_id:
#             return Response({"detail": "Driver ID is required."}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             driver = User.objects.get(id=driver_id, user_type='driver')
#         except User.DoesNotExist:
#             return Response({"detail": "Driver not found."}, status=status.HTTP_404_NOT_FOUND)
#
#         # Assign the driver to the load and update status
#         load.driver = driver
#         load.status = 'assigned'
#         load.save()
#
#         return Response({"detail": "Load assigned to driver successfully."}, status=status.HTTP_200_OK)

#
# class CreateAssignmentView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]  # Only Admins can assign loads
#
#     def post(self, request):
#         # Ensure the user is an admin or dispatcher
#         if request.user.user_type not in ['admin', 'dispatcher']:
#             return Response({"detail": "You do not have permission to assign loads."}, status=status.HTTP_403_FORBIDDEN)
#
#         serializer = AssignmentSerializer(data=request.data)
#
#         if serializer.is_valid():
#             # Save the assignment and return the response
#             serializer.save(dispatcher=request.user)  # Associate the current user as the dispatcher
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def put(self, request, assignment_id):
#         try:
#             assignment = Assignment.objects.get(id=assignment_id)
#         except Assignment.DoesNotExist:
#             return Response({"detail": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)
#
#         # Check if the user is authorized
#         if request.user.user_type not in ['admin', 'dispatcher']:
#             return Response({"detail": "You do not have permission to update assignments."},
#                             status=status.HTTP_403_FORBIDDEN)
#
#         serializer = AssignmentSerializer(assignment, data=request.data, partial=True)
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CreateAssignmentView(APIView):
#     permission_classes = [IsAuthenticated]  # Allow both admins and dispatchers to assign loads
#
#     def post(self, request):
#         # Ensure the user is either an admin or dispatcher
#         if request.user.user_type not in ['admin', 'dispatcher']:
#             return Response({"detail": "You do not have permission to assign loads."}, status=status.HTTP_403_FORBIDDEN)
#
#         # Validate the driver exists and is of the correct type
#         driver_id = request.data.get('driver')
#         try:
#             driver = User.objects.get(id=driver_id, user_type='driver')
#         except User.DoesNotExist:
#             return Response({"detail": "Invalid driver ID - driver does not exist."}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Assign the dispatcher to the current authenticated user
#         dispatcher = request.user  # The current logged-in user is the dispatcher
#
#         # Add the dispatcher to the request data (this is passed to the serializer)
#         data = {
#             **request.data,
#             'dispatcher': dispatcher.id  # Automatically set the dispatcher ID
#         }
#
#         # Create and validate the assignment
#         serializer = AssignmentSerializer(data=data)
#         if serializer.is_valid():
#             # Save the assignment
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateAssignmentView(APIView):
    permission_classes = [IsAuthenticated]  # Allow both admins and dispatchers to assign loads

    def post(self, request):
        # Ensure the user is either an admin or dispatcher
        if request.user.user_type not in ['admin', 'dispatcher']:
            return Response({"detail": "You do not have permission to assign loads."},
                            status=status.HTTP_403_FORBIDDEN)

        # Validate the driver exists and is of the correct type
        driver_id = request.data.get('driver')
        try:
            driver = User.objects.get(id=driver_id, user_type='driver')
        except User.DoesNotExist:
            return Response({"detail": "Invalid driver ID - driver does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate the load exists and is unassigned
        load_id = request.data.get('load')
        try:
            load = Load.objects.get(id=load_id)
        except Load.DoesNotExist:
            return Response({"detail": "Invalid load ID - load does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        if load.status != 'unassigned':
            return Response({"detail": "The load is already assigned or completed."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Assign the dispatcher to the current authenticated user
        dispatcher = request.user  # The current logged-in user is the dispatcher

        # Add the dispatcher to the request data (this is passed to the serializer)
        data = {
            **request.data,
            'dispatcher': dispatcher.id,  # Automatically set the dispatcher ID
        }

        # Create and validate the assignment
        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            # Save the assignment
            assignment = serializer.save()

            # Update the status of the load to "assigned"
            load.status = 'assigned'
            load.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, assignment_id):
        # Update the assignment (with PUT method)
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response({"detail": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the user is an admin or dispatcher to update
        if request.user.user_type not in ['admin', 'dispatcher']:
            return Response({"detail": "You do not have permission to update assignments."},
                            status=status.HTTP_403_FORBIDDEN)

        # Update the assignment data
        serializer = AssignmentSerializer(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def chatroom(request):
    # Render the chatroom template
    return render(request, 'chat.html')




class IndividualChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, target_user_id):
        # Get the authenticated user
        user = request.user

        # Fetch messages between the authenticated user and the target user
        messages = Message.objects.filter(
            (Q(sender=user) & Q(receiver=target_user_id)) | (Q(sender=target_user_id) & Q(receiver=user))
        ).order_by('created_at')

        # Serialize the messages
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, target_user_id):
        # Get the authenticated user (sender)
        sender = request.user

        # Get the receiver (target user) using the provided target_user_id
        receiver = get_object_or_404(User, id=target_user_id)

        # Get the message from the request data
        message = request.data.get('message')

        # Create a new message object and assign the sender and receiver
        new_message = Message.objects.create(
            sender=sender,  # The authenticated user is the sender
            receiver=receiver,  # The target user is the receiver
            message=message
        )

        # Serialize and return the created message
        serializer = MessageSerializer(new_message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CheckInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Ensure the user is a driver
        if request.user.user_type != 'driver':
            return Response({"detail": "You do not have permission to check in."}, status=status.HTTP_403_FORBIDDEN)

        # Create a check-in record
        check_in = CheckInOut.objects.create(
            driver=request.user,  # Automatically assign the authenticated user as the driver
            check_in_time=timezone.now()
        )

        # Serialize and return the check-in data
        serializer = CheckInOutSerializer(check_in)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Ensure the user is a driver
        if request.user.user_type != 'driver':
            return Response({"detail": "You do not have permission to check out."}, status=status.HTTP_403_FORBIDDEN)

        # Fetch the most recent check-in record for the driver
        check_in_out = CheckInOut.objects.filter(driver=request.user, check_out_time__isnull=True).last()

        if not check_in_out:
            return Response({"detail": "No active check-in record found."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the check-out time
        check_in_out.check_out_time = timezone.now()
        check_in_out.save()

        # Serialize and return the updated check-in/out data
        serializer = CheckInOutSerializer(check_in_out)
        return Response(serializer.data, status=status.HTTP_200_OK)