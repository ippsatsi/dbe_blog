from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

# Create your views here.
class PostListView(ListView):
    """
    Alternativa post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    post_list = Post.published.all()
    #pagination with 3 posts per page
    paginator = Paginator(post_list,3)
    page_number = request.GET.get('page',1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # Si page_number no es un entero
        posts = paginator.page(1)
    except EmptyPage:
        #Si page_number esta fuera del rango de la ultima pagina de resultados
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html',
                  {'posts':posts})


def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404('No Post found.')
    post = get_object_or_404(Post,
                            #  id=id,
                            slug=post,
                            publish__year=year,
                            publish__month=month,
                            publish__day=day,
                            status=Post.Status.PUBLISHED)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post})


