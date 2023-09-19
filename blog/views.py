from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostFrom, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST


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


def post_share(request, post_id):
    #Recuperar post x id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # Form fue enviado
        form = EmailPostFrom(request.POST)
        if form.is_valid():
            # Campos del form pasaron validacion
            cd = form.cleaned_data
            # enviamos email
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} le recomienda leer " \
                        f"{post.title}"
            message = f"Leer {post.title} en {post_url}\n\n" \
                        f"comentarios de {cd['name']}: {cd['comments']}"
            send_mail(subject, message, 'laz133@gmail.com',
                      [cd['to']])
            sent = True
    else:
        form = EmailPostFrom()
    return render(request, 'blog/post/share.html', {'post':post,
                                                    'form': form,
                                                    'sent': sent})


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
    # list of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    #Un cometario fue posteado
    form = CommentForm(data=request.POST)
    if form.is_valid():
        #Crear un objeto comentario sin salvarloa a la DB
        comment = form.save(commit=False)
        # Asignamos el post al comentario 
        comment.post = post
        # Guardamos el comentario en la DB
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})
