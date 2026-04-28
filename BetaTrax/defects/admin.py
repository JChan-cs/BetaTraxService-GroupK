from django.contrib import admin
from django.contrib.auth.models import User
from .models import DefectReport, Comment, DeveloperMetrics  # Added DeveloperMetrics
from products.models import Product
from .developer_metrics import classify_effectiveness  # Import logic for display

@admin.register(DeveloperMetrics)
class DeveloperMetricsAdmin(admin.ModelAdmin):
    """
    Admin interface for tracking and manually adjusting developer performance metrics.
    """
    list_display = ("user", "defects_fixed", "defects_reopened", "get_effectiveness_rating", "get_ratio")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    list_filter = ("defects_fixed", "defects_reopened")
    
    # We make the calculated effectiveness read-only in the edit form
    readonly_fields = ("get_effectiveness_rating", "get_ratio")

    def get_effectiveness_rating(self, obj):
        """Displays the 'Good/Fair/Poor' rating based on current stats."""
        rating, _ = classify_effectiveness(obj.defects_fixed, obj.defects_reopened)
        return rating
    get_effectiveness_rating.short_description = "Effectiveness Rating"

    def get_ratio(self, obj):
        """Displays the raw reopened/fixed ratio."""
        _, ratio = classify_effectiveness(obj.defects_fixed, obj.defects_reopened)
        return ratio if ratio is not None else "N/A"
    get_ratio.short_description = "Reopened Ratio"

    fieldsets = (
        ("User Info", {
            "fields": ("user",)
        }),
        ("Statistics", {
            "fields": ("defects_fixed", "defects_reopened")
        }),
        ("Calculated Metrics", {
            "fields": ("get_effectiveness_rating", "get_ratio"),
            "description": "These values are calculated automatically based on the statistics above."
        }),
    )


@admin.register(DefectReport)
class DefectReportAdmin(admin.ModelAdmin):
    class CommentInline(admin.TabularInline):
        model = Comment
        extra = 1
        fields = ('author', 'text', 'created_at')

        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            if db_field.name == "author":
                resolved = request.resolver_match
                if resolved and 'object_id' in resolved.kwargs:
                    try:
                        defect = DefectReport.objects.get(pk=resolved.kwargs['object_id'])
                        allowed_users = []
                        if defect.assigned_to:
                            allowed_users.append(defect.assigned_to.id)
                        try:
                            product = Product.objects.get(product_id=defect.ProductID)
                            allowed_users.append(product.product_owner.id)
                        except Product.DoesNotExist:
                            pass
                        kwargs["queryset"] = User.objects.filter(id__in=allowed_users)
                    except DefectReport.DoesNotExist:
                        kwargs["queryset"] = User.objects.none()
                else:
                    kwargs["queryset"] = User.objects.none()
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
    list_display = ("ProductID", "ReportTitle", "Status", "assigned_to", "CreatedTime", "TesterID")
    inlines = [CommentInline]
    list_display_links = ("ProductID", "ReportTitle")
    list_filter = ("Status", "Severity", "Priority", "CreatedTime", "assigned_to")
    search_fields = ("ReportTitle", "Description", "TesterID", "ProductID")
    readonly_fields = ("UpdatedTime",) 
    
    fieldsets = (
        ("Product Info", {
            "fields": ("ProductID", "Version", "ReportTitle", "Description", "Steps", "Status", "Severity", "Priority")
        }),
        ("Assignment", {
            "fields": ("assigned_to",)
        }),
        ("Tester Info", {
            "fields": ("TesterID", "Email")
        }),
        ("Time", {
            "fields": ("CreatedTime", "UpdatedTime")
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            kwargs["queryset"] = User.objects.filter(groups__name="Developer")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)