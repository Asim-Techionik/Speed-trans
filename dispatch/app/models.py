from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings




USER_TYPE_CHOICES = (
    ('dispatcher', 'Dispatcher'),
    ('driver', 'Driver'),
    ('admin', 'Admin'),
)

# class CustomUser(AbstractUser):
#     username = None  # Remove the username field
#     email = models.EmailField(unique=True)
#     user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True, null=True)  # Optional user type
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []  # No required fields during user creation, as email is the only required one
#
#     def __str__(self):
#         return f"{self.email} ({self.user_type})"

class CustomUser(AbstractUser):
    # User Type
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True, null=True)

    # Fields for Dispatchers
    profile = models.FileField(upload_to='Profile/', blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=(('male', 'Male'), ('female', 'Female'), ('other', 'Other')), blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    location_branch = models.CharField(max_length=255, blank=True, null=True)

    # Fields for Drivers
    phone_number_driver = models.CharField(max_length=15, blank=True, null=True)
    total_loads = models.IntegerField(default=0, blank=True, null=True)
    completed_loads = models.IntegerField(default=0, blank=True, null=True)
    license_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    license_expiry = models.DateField(blank=True, null=True)
    vehicle_type = models.CharField(max_length=20, choices=(('car', 'Car'), ('truck', 'Truck'), ('van', 'Van'), ('motorcycle', 'Motorcycle'), ('other', 'Other')), blank=True, null=True)
    vehicle_plate_no = models.CharField(max_length=20, blank=True, null=True)
    driver_license = models.FileField(upload_to='driver_licenses/', blank=True, null=True)
    vehicle_registration = models.FileField(upload_to='vehicle_registrations/', blank=True, null=True)

    # Override username field to be email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # email is required, username, and user_type as optional

    def __str__(self):
        return f"{self.email} ({self.user_type})"


# Override create_user method to ensure it doesn't require username
    @classmethod
    def create_user(cls, email, password, user_type=None, **extra_fields):
        """
        Creates and returns a user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = email.lower()
        user = cls(email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save()  # Let Django handle saving the object
        return user


User = get_user_model()


class Load(models.Model):
    LOAD_STATUS_CHOICES = (
        ('unassigned', 'Unassigned'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )

    loadname = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    weight_lbs = models.DecimalField(max_digits=10, decimal_places=2)  # Weight in pounds
    status = models.CharField(max_length=20, choices=LOAD_STATUS_CHOICES, default='pending')
    document = models.FileField(upload_to='load_documents/', blank=True, null=True)  # Field for images/PDFs

    # ForeignKey to associate load with dispatcher and driver
    # dispatcher = models.ForeignKey(User, related_name="created_loads", on_delete=models.CASCADE,
    #                                limit_choices_to={'user_type': 'dispatcher'})
    admin = models.ForeignKey(User, related_name="admin_loads", on_delete=models.SET_NULL, blank=True, null=True,
                              limit_choices_to={'user_type': 'admin'})

    def __str__(self):
        return f"{self.loadname} - {self.status} - {self.dispatcher.email}"




# class Dispatcher(models.Model):
#     GENDER_CHOICES = (
#         ('male', 'Male'),
#         ('female', 'Female'),
#         ('other', 'Other'),
#     )
#
#     first_name = models.CharField(max_length=100, blank=True, null=True)  # Optional
#     last_name = models.CharField(max_length=100, blank=True, null=True)  # Optional
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=255)  # Password is required
#     gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)  # Optional
#     dob = models.DateField(blank=True, null=True)  # Optional Date of Birth
#     address = models.TextField(blank=True, null=True)  # Optional
#     phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional
#     username = models.CharField(max_length=150, unique=True, blank=True, null=True)  # Optional
#     location_branch = models.CharField(max_length=255, blank=True, null=True)  # Optional
#
#     def __str__(self):
#         return f"{self.first_name} {self.last_name} - {self.username}"
#
#
#
#
# class Driver(models.Model):
#     VEHICLE_TYPE_CHOICES = (
#         ('car', 'Car'),
#         ('truck', 'Truck'),
#         ('van', 'Van'),
#         ('motorcycle', 'Motorcycle'),
#         ('other', 'Other'),
#     )
#
#     first_name = models.CharField(max_length=100, blank=True, null=True)  # Optional
#     last_name = models.CharField(max_length=100, blank=True, null=True)  # Optional
#     phone_number_driver = models.CharField(max_length=15, blank=True, null=True)  # Optional
#     email = models.EmailField(unique=True)
#     total_loads = models.IntegerField(default=0, blank=True, null=True)  # Optional
#     completed_loads = models.IntegerField(default=0, blank=True, null=True)  # Optional
#     license_number = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Optional
#     license_expiry = models.DateField(blank=True, null=True)  # Optional
#     vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, blank=True, null=True)  # Optional
#     vehicle_plate_no = models.CharField(max_length=20, blank=True, null=True)  # Optional
#     driver_license = models.FileField(upload_to='driver_licenses/', blank=True, null=True)  # Optional
#     vehicle_registration = models.FileField(upload_to='vehicle_registrations/', blank=True, null=True)  # Optional
#
#     def __str__(self):
#         return f"{self.first_name} {self.last_name} - {self.license_number}"

class Assignment(models.Model):
    ASSIGNMENT_STATUS_CHOICES = (
        ('unassigned', 'Unassigned'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )

    load = models.ForeignKey(Load, related_name="assignments", on_delete=models.CASCADE)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="driver_assignments", on_delete=models.CASCADE, limit_choices_to={'user_type': 'driver'})
    dispatcher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="dispatcher_assignments", on_delete=models.CASCADE, limit_choices_to={'user_type': 'dispatcher'}, blank=True, null=True)
    assignment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='unassigned')

    def __str__(self):
        return f"Assignment for {self.load.loadname} to {self.driver.email} - {self.status}"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.created_at}"


class CheckInOut(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="check_in_outs", limit_choices_to={'user_type': 'driver'})
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CheckInOut for {self.driver.email} at {self.created_at}"


