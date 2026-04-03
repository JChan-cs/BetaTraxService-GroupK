from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import CommentForm

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    
    return render(request, 'post_detail.html', {'post': post, 'comments': comments, 'form': form})
