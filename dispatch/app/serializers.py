from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Load, Assignment, Message, CheckInOut


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password', 'user_type']  # Only email, password, and user_type are required
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        # Validate the password strength
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        # Set is_staff and is_superuser based on user_type
        user_type = validated_data.get('user_type', 'driver')  # Default to 'driver' if not provided
        is_staff = is_superuser = False

        if user_type == 'admin':
            is_staff = True
            is_superuser = True

        # Create the user using the overridden create_user method
        user = User.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type'],
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        return user


# class UserListSerializer(serializers.ModelSerializer):
#     # Include any other fields you want to expose in the list (first_name, last_name, etc.)
#     class Meta:
#         model = User
#         fields = ['id','email', 'user_type', 'first_name', 'last_name', 'phone_number', 'location_branch', 'is_active', 'phone_number_driver', 'total_loads', 'completed_loads']  # Add other fields as necessary


class DriverListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'first_name', 'last_name', 'phone_number_driver', 'total_loads', 'completed_loads']


class DispatcherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'first_name', 'last_name', 'phone_number', 'location_branch']


# class LoadSerializer(serializers.ModelSerializer):
#     # Including the dispatcher, driver, and admin info
#     dispatcher_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='dispatcher'), write_only=True)
#     admin_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='admin'), required=False, write_only=True)
#
#     class Meta:
#         model = Load
#         fields = ['loadname', 'pickup_location', 'delivery_location', 'pickup_date', 'pickup_time', 'delivery_date', 'delivery_time', 'weight_lbs', 'status', 'document', 'admin_id']
#         extra_kwargs = {
#             'status': {'default': 'unassigned'},  # By default, set the load as unassigned
#             # 'dispatcher': {'read_only': True},  # Make sure dispatcher is read-only since it's assigned by the view
#         }
#
#     def create(self, validated_data):
#         #dispatcher_id = validated_data.pop('dispatcher_id')
#         admin_id = validated_data.pop('admin_id', None)
#
#         # Fetch the dispatcher, driver, and admin instances from the database
#         #dispatcher = User.objects.get(id=dispatcher_id)
#         driver = None
#
#         admin = None
#         if admin_id:
#             admin = User.objects.get(id=admin_id)
#
#         # Create the load instance with dispatcher, driver, and optional admin
#         load = Load.objects.create(driver=driver, admin=admin, **validated_data)
#         return load


class LoadSerializer(serializers.ModelSerializer):
    # Admin information is extracted from the authenticated user (no need to pass it in the request)
    class Meta:
        model = Load
        fields = ['loadname', 'pickup_location', 'delivery_location', 'pickup_date', 'pickup_time', 'delivery_date', 'delivery_time', 'weight_lbs', 'status', 'document']
        extra_kwargs = {
            'status': {'default': 'unassigned'},  # By default, set the load as unassigned
        }

    def create(self, validated_data):
        # Get the authenticated user from the request (which should be an admin)
        user = self.context['request'].user

        # Ensure the user is an admin
        if user.user_type != 'admin':
            raise serializers.ValidationError("Only admins can create loads.")

        # The admin is automatically associated with the load (no need to pass it)
        load = Load.objects.create(admin=user, **validated_data)
        return load


class AssignmentSerializer(serializers.ModelSerializer):
    load = serializers.PrimaryKeyRelatedField(queryset=Load.objects.all())
    driver = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='driver'))
    # dispatcher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='dispatcher'))

    class Meta:
        model = Assignment
        fields = ['id', 'load', 'driver', 'assignment_date', 'status']

    def create(self, validated_data):
        # Create the assignment
        assignment = Assignment.objects.create(**validated_data)
        return assignment


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'message', 'created_at']
        read_only_fields = ['created_at']  # Don't allow updating the created_at field


class CheckInOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInOut
        fields = ['id', 'driver', 'check_in_time', 'check_out_time', 'created_at']

# class CheckInOutSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CheckInOut
#         fields = ['id', 'user', 'check_in_time', 'check_out_time', 'created_at']


class CheckInOutSerializer(serializers.ModelSerializer):
    total_hours_worked = serializers.SerializerMethodField()

    class Meta:
        model = CheckInOut
        fields = ['id', 'driver', 'check_in_time', 'check_out_time', 'created_at', 'total_hours_worked']

    def get_total_hours_worked(self, obj):
        if obj.check_out_time and obj.check_in_time:
            # Calculate the difference between check-in and check-out times
            duration = obj.check_out_time - obj.check_in_time
            return str(duration.total_seconds() / 3600)  # Convert seconds to hours
        return 0

# Dispatcher Serializer
class DispatcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile', 'first_name', 'last_name', 'email', 'gender', 'dob', 'address',
                  'phone_number', 'username', 'location_branch', 'years_experience', 'employee_id',
                  'id_card', 'work_certification', 'training_certification']

# Driver Serializer
class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile', 'first_name', 'last_name', 'email', 'gender', 'dob', 'address',
                  'phone_number_driver', 'total_loads', 'completed_loads', 'license_number',
                  'license_expiry', 'vehicle_type', 'vehicle_plate_no', 'driver_license',
                  'vehicle_registration']