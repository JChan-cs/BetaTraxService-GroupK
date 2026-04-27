from django.contrib import admin
from django.contrib.auth.models import User
from .models import DefectReport, Comment
from products.models import Product  # Import models directly

@admin.register(DefectReport)
class DefectReportAdmin(admin.ModelAdmin):
    class CommentInline(admin.TabularInline):
        model = Comment
        extra = 1
        fields = ('author', 'text', 'created_at')

        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            """
            Restricts the 'author' dropdown to only the Product Owner 
            and the Developer assigned to this specific defect.
            """
            if db_field.name == "author":
                # Extract the DefectReport ID from the URL (e.g., /admin/app/defectreport/5/change/)
                resolved = request.resolver_match
                if resolved and 'object_id' in resolved.kwargs:
                    try:
                        defect = DefectReport.objects.get(pk=resolved.kwargs['object_id'])
                    
                        # 1. Get the Responsible Developer
                        allowed_users = []
                        if defect.assigned_to:
                            allowed_users.append(defect.assigned_to.id)
                    
                        # 2. Get the Product Owner
                        # We look up the Product using the ProductID string from the DefectReport
                        try:
                            product = Product.objects.get(product_id=defect.ProductID)
                            allowed_users.append(product.product_owner.id)
                        except Product.DoesNotExist:
                            pass
                    
                        # Filter the queryset to only these users
                        kwargs["queryset"] = User.objects.filter(id__in=allowed_users)
                    except DefectReport.DoesNotExist:
                        kwargs["queryset"] = User.objects.none()
                else:
                    # If it's a brand new DefectReport (no ID yet), we can't determine 
                    # owner/developer, so we show an empty list or all users.
                    kwargs["queryset"] = User.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
    # Added 'assigned_to' to the list view for visibility
    list_display = ("ProductID", "ReportTitle", "Status", "assigned_to", "CreatedTime", "TesterID")
    inlines = [CommentInline] # Show comments at the bottom
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