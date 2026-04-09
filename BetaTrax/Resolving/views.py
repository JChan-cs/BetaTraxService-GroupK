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
            
        return queryset
    
@login_required
@user_passes_test(is_product_owner)
def update_retest_status(request, pk):
    result = get_object_or_404(Result, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status') 
        
        if new_status in ['Resolved', 'Reopened']:
            result.retest_result = new_status

            # Update the status of the associated DefectReport
            defect = get_object_or_404(DefectReport, pk=result.report_id)
            serializer = DefectReportStatusSerializer(instance=defect, data={'Status': new_status}, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            result.save()
            Comment.objects.create(
                author = request.user, 
                text=f"System Update: Report #{result.report_id} has been marked as {new_status} by {request.user.username}."
            )

            messages.success(request, f"Report {result.report_id} updated to {new_status} and announced.")
            return redirect('result-list')
            
    return render(request, 'Resolving/update_status.html', {'result': result})