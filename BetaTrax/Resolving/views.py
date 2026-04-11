from django.views.generic import ListView
from .models import Result 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from comments.models import Comment
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test

from defects.serializers import DefectReportStatusSerializer
from defects.models import DefectReport

def is_product_owner(user):
    return user.groups.filter(name='ProductOwner').exists()

class ResultListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Result
    template_name = 'Resolving/retest_list.html'
    context_object_name = 'retest'
    paginate_by = 10

    def test_func(self):
        # Only PO can access
        return self.request.user.groups.filter(name='ProductOwner').exists()

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-date')
        report_id = self.request.GET.get('report_id')
        search_date = self.request.GET.get('date')
        result = self.request.GET.get('retest_result')

        if report_id:
            queryset = queryset.filter(report_id__icontains=report_id)
        if search_date:
            queryset = queryset.filter(date=search_date)
        if result:
            queryset = queryset.filter(retest_result=result)
            
        # Convert to list so we can attach a computed attribute for template use.
        # ListView's paginator accepts sequences, so returning a list is fine here.
        results = list(queryset)

        # Build a mapping from report_id to current DefectReport.Status where possible.
        report_ids = [r.report_id for r in results]
        # Normalize to strings (Result.report_id is stored as CharField)
        report_ids = [str(rid) for rid in report_ids if rid is not None]
        if report_ids:
            defects = DefectReport.objects.filter(pk__in=report_ids)
            defect_map = {str(d.pk): d for d in defects}
        else:
            defect_map = {}

        for r in results:
            # Prefer the live Status from DefectReport if available; fall back to stored retest_result
            defect = defect_map.get(str(r.report_id))
            r.current_status = getattr(defect, 'Status', None) if defect else r.retest_result

        return results
    
@login_required
@user_passes_test(is_product_owner)
def update_retest_status(request, pk):
    result = get_object_or_404(Result, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status') 
        
        if new_status in ['Resolved', 'Reopened']:
            # Update the status of the associated DefectReport
            defect = get_object_or_404(DefectReport, pk=result.report_id)
            # pass assigned_to as a primary key (or None) because the serializer
            # expects a PK value for relational fields when receiving input data
            assigned_pk = defect.assigned_to.pk if (hasattr(defect, 'assigned_to') and defect.assigned_to) else None
            serializer = DefectReportStatusSerializer(
                instance=defect,
                data={'Status': new_status, 'assigned_to': assigned_pk},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Ensure the Result.retest_result mirrors the saved DefectReport.Status
            # (use the serializer.instance which is the updated model)
            updated_defect = serializer.instance
            result.retest_result = getattr(updated_defect, 'Status', new_status)
            result.save()
            Comment.objects.create(
                defect = defect,
                author = request.user, 
                text=f"System Update: Report #{result.report_id} has been marked as {new_status} by {request.user.username}."
            )

            messages.success(request, f"Report {result.report_id} updated to {new_status} and announced.")
            return redirect('result-list')
            
    return render(request, 'Resolving/update_status.html', {'result': result})