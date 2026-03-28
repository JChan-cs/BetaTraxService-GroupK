from django.contrib import admin
from .models import DefectReport

admin.site.register(DefectReport)


class DefectReportAdmin(admin.ModelAdmin):
    list_display = ("ProductID", "ReportTitle", "Status", "CreatedTime", "TesterID")
    list_display_links = ("ProductID", "Report Title")
    list_filter = ("Status", "Severity", "Priority", "CreatedTime")
    search_fields = ("ReportTitle", "Description", "TesterID", "ProductID")
    readonly_fields = ("CreatedTime", "UpdatedTime")
    fieldsets = (
        ("Product Info", {"fields": ("ProductID", "Version", "ReportTitle", "Description", "Steps", "Status", "Severity", "Priority")}),
        ("Tester Info", {"fields": ("TesterID", "Email")}),
        ("Time", {"fields": ("CreatedTime", "UpdatedTime")}),
    )
