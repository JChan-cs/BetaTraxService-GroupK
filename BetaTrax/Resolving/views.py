from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test

from comments.models import Comment
from defects.serializers import DefectReportStatusSerializer
from defects.models import DefectReport

def is_product_owner(user):
    return user.groups.filter(name='ProductOwner').exists()

class ResultListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = DefectReport
    template_name = 'Resolving/result_list.html'
    context_object_name = 'retest'
    paginate_by = 10

    def test_func(self):
        # Only PO can access
        return self.request.user.groups.filter(name='ProductOwner').exists()

    def get_queryset(self):
        queryset = super().get_queryset().filter(Status="Fixed").order_by('-UpdatedTime')
        report_id = self.request.GET.get('report_id')
        search_date = self.request.GET.get('date')
        status_query = self.request.GET.get('retest_result')

        if report_id:
            if report_id.isdigit():
                queryset = queryset.filter(pk=int(report_id))
            else:
                queryset = queryset.filter(ReportTitle__icontains=report_id)
        if search_date:
            queryset = queryset.filter(UpdatedTime__date=search_date)
        if status_query:
            queryset = queryset.filter(Status__iexact=status_query)

        return queryset
    
@login_required
@user_passes_test(is_product_owner)
def update_retest_status(request, pk):
    defect = get_object_or_404(DefectReport, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status') 
        
        if new_status in ['Resolved', 'Reopened']:
            # Update the status of the associated DefectReport
            serializer = DefectReportStatusSerializer(instance=defect, data={'Status': new_status}, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            Comment.objects.create(
                author = request.user, 
                defect=defect,
                text=f"System Update: Defect #{defect.pk} has been marked as {new_status} by {request.user.username}."
            )

            messages.success(request, f"Defect {defect.pk} updated to {new_status} and announced.")
            return redirect('result-list')
    return render(request, 'Resolving/update_status.html', {'defect': defect})