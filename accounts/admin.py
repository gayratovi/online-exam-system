# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser, Module
from exams.models import Exam

# Remove Groups from admin
admin.site.unregister(Group)

# Change admin site headers and titles
admin.site.site_header = "CSSS Administration"
admin.site.site_title = "CSSS Admin Portal"
admin.site.index_title = "Welcome to the Computer Science Success School Admin"

# -------------------------------
# Proxy models for clarity
# -------------------------------
class Student(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Student"
        verbose_name_plural = "Students"

class Staff(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Staff"
        verbose_name_plural = "Staff"

class AdminUser(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Admin"
        verbose_name_plural = "Admin"

# -------------------------------
# Inlines
# -------------------------------
class ExamInline(admin.TabularInline):
    model = Exam
    fk_name = "module"
    extra = 0
    show_change_link = True

# -------------------------------
# Student admin (M2M modules)
# -------------------------------
@admin.register(Student)
class StudentAdmin(UserAdmin):
    model = Student

    list_display = ("username", "email", "enrolled_modules", "is_active", "last_login")
    list_filter = ("is_active", "modules")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    # Use horizontal selector for ManyToMany
    filter_horizontal = ("modules",)

    # Keep standard UserAdmin fieldsets + our custom section
    fieldsets = UserAdmin.fieldsets + (
        ("Enrollment", {"fields": ("modules",)}),
    )

    # Role should not be editable here; force to 'student'
    readonly_fields = ("role",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role="student").prefetch_related("modules")

    def enrolled_modules(self, obj):
        names = list(obj.modules.values_list("code", flat=True))
        return ", ".join(names) if names else "—"
    enrolled_modules.short_description = "Modules"

    def save_model(self, request, obj, form, change):
        obj.role = "student"  # enforce role
        super().save_model(request, obj, form, change)

# -------------------------------
# Staff admin (single module FK)
# -------------------------------
@admin.register(Staff)
class StaffAdmin(UserAdmin):
    model = Staff

    list_display = ("username", "email", "module", "is_active", "last_login")
    list_filter = ("is_active", "module")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        ("Teaching", {"fields": ("module",)}),
    )

    readonly_fields = ("role",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role="staff").select_related("module")

    def save_model(self, request, obj, form, change):
        obj.role = "staff"  # enforce role
        super().save_model(request, obj, form, change)

# -------------------------------
# Module admin
# -------------------------------
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "staff_count", "student_count")
    search_fields = ("code", "name")
    inlines = [ExamInline]

    def staff_count(self, obj):
        return obj.staff_members.count()
    staff_count.short_description = "Staff"

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = "Students"

@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    model = AdminUser

    list_display = ("username", "email", "is_superuser", "is_active", "last_login")
    list_filter = ("is_active", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    readonly_fields = ("role",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role="admin")

    def save_model(self, request, obj, form, change):
        obj.role = "admin"  # enforce role
        obj.is_staff = True
        obj.is_superuser = True
        super().save_model(request, obj, form, change)