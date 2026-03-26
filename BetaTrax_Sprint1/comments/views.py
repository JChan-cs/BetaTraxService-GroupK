from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.shortcuts import redirect
from .models import Comment
from django.db.models import Q

class CommentListView(ListView):
    model = Comment
    template_name = 'comments/comment_list.html'
    context_object_name = 'comments'
    paginate_by = 25

    def get_queryset(self):
        queryset = Comment.objects.select_related('author').all().order_by('-created_at')
        query = self.request.GET.get('q')
        search_date = self.request.GET.get('date')

        if query:
            queryset = queryset.filter(
                Q(text__icontains=query) | Q(author__username__icontains=query)
            )
        if search_date:
            queryset = queryset.filter(created_at__date=search_date)
        return queryset

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to post.")
            return redirect('comment-list')

        comment_text = request.POST.get('text')
        if comment_text:
            # Simply create the comment with the author and text
            Comment.objects.create(
                author=request.user,
                text=comment_text
            )
            messages.success(request, "Comment added!")
        
        return redirect('comment-list')

class CommentDetailView(DetailView):
    model = Comment
    template_name = 'comments/comment_detail.html'
    context_object_name = 'comment'
