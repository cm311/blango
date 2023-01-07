import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from blog.models import Post
from blog.forms import CommentForm


#create a module-level logging variable.  Can be used to add logger calls
logger = logging.getLogger(__name__)

# Create your views here.


#@cache_page(300)

#params are names of the headers that will cause the response to vary
#@vary_on_headers("Cookie")
def index(request):
  #Post object only queried every 300 seconds, all other responses come
  #from cache.  Dont cache stuff whose content relies on logged in user.
  #from django.http import HttpResponse
  #return HttpResponse(str(request.user).encode("ascii"))
  #only load posts that have a publication date in the past
  posts = Post.objects.filter(published_at__lte=timezone.now())
  logger.debug("Got %d posts", len(posts))
  return render(request, "blog/index.html", {"posts": posts})
  
def post_detail(request, slug):
  post = get_object_or_404(Post, slug=slug)
  
  if request.user.is_active:
    if request.method == "POST":
      comment_form = CommentForm(request.POST)

      if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.content_object = post
        comment.creator = request.user
        comment.save()
        logger.info("Created comment on Post %d for user %s", post.pk, request.user)
        return redirect(request.path_info)
      
    else:
      comment_form = CommentForm()

  else:
    comment_form = None

  return render(request, "blog/post-detail.html", {"post": post, "comment_form" : comment_form})


