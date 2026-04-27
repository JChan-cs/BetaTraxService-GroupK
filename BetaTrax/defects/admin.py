from django.contrib import admin
from django.contrib.auth.models import User
from .models import DefectReport

@admin.register(DefectReport)
class DefectReportAdmin(admin.ModelAdmin):
    # Added 'assigned_to' to the list view for visibility
    list_display = ("ProductID", "ReportTitle", "Status", "assigned_to", "CreatedTime", "TesterID")
    list_display_links = ("ProductID", "ReportTitle")
    list_filter = ("Status", "Severity", "Priority", "CreatedTime", "assigned_to")
    search_fields = ("ReportTitle", "Description", "TesterID", "ProductID")
    
    # 'CreatedTime' is removed from readonly_fields per your previous request
    readonly_fields = ("UpdatedTime",) 
    
    fieldsets = (
        ("Product Info", {
            "fields": ("ProductID", "Version", "ReportTitle", "Description", "Steps", "Status", "Severity", "Priority")
        }),
        ("Assignment", {
            "fields": ("assigned_to",) # Added the assignment field here
        }),
        ("Tester Info", {
            "fields": ("TesterID", "Email")
        }),
        ("Time", {
            "fields": ("CreatedTime", "UpdatedTime")
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Optional: Filters the 'assigned_to' dropdown to only show 
        users in the 'Developer' group.
        """
        if db_field.name == "assigned_to":
            kwargs["queryset"] = User.objects.filter(groups__name="Developer")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)