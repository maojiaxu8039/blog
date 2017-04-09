from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from  django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from .forms import EmailPostForm, CommentForm, SearchForm
from haystack.query import SearchQuerySet


class PostListView(ListView):
    queryset = Post.published.all()
    # 使用环境变量posts给查询结果。如果我们不指定任意的context_object_name默认的变量将会是object_list
    context_object_name = 'posts'
    # 对结果进行分页处理每页只显示4个对象。
    paginate_by = 4
    # 使用定制的模板（template）来渲染页面。如果我们不设置默认的模板（template），ListView将会使用blog/post_list.html
    template_name = 'blog/post/list.html'


# def post_list(request):
#     posts = Post.published.all()
#     return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    # get_object_or_404()快捷方法来检索期望的Post。这个函数能取回匹配给予的参数的对象，或者当没有匹配的对象时返回一个HTTP 404（Not found）异常
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # 如果你调用这个方法时设置commit=False，你创建的模型（model）实例不会即时保存到数据库中
            new_comment = comment_form.save(commit=False)
            # 创建的评论分配一个帖子
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    # 我们取回了一个包含当前帖子所有标签的ID的Python列表。values_list() 查询集（QuerySet）返回包含给定的字段值的元祖。
    # 我们传给元祖flat=True来获取一个简单的列表类似[1,2,3,...]
    post_tag_ids = post.tags.values_list('id', flat=True)
    # django-taggit还内置了一个similar_objects() 管理器（manager）使你可以通过共享的标签返回所有对象
    # print(post.tags.similar_objects())
    # 我们获取所有包含这些标签的帖子排除了当前的帖子。
    similar_posts = Post.published.filter(tags__in=post_tag_ids).exclude(id=post.id)
    # 我们使用Count聚合函数来生成一个计算字段same_tags，该字段包含与查询到的所有 标签共享的标签数量。
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts})


def post_list(request, tag_slug=None):
    """
    我们使用希望在每页中显示的对象的数量来实例化Paginator类。
    我们获取到page GET参数来指明页数
    我们通过调用Paginator的 page()方法在期望的页面中获得了对象。
    如果page参数不是一个整数，我们就返回第一页的结果。如果这个参数数字超出了最大的页数，我们就展示最后一页的结果。
    我们传递页数并且获取对象给这个模板（template）。
    :param tag_slug:带有一个可选的tag_slug参数，默认是一个None值。这个参数会带进URL中
    :return:
    """
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # 当用户填写好了表单并通过POST提交表单。之后，我们会用保存在request.POST中提交的数据创建一个表单实例
        form = EmailPostForm(request.POST)
        # 表单的is_valid()方法来验证提交的数据。这个方法会验证表单引进的数据，如果所有的字段都是有效数据，将会返回True。
        # 一旦有任何一个字段是无效的数据，is_valid()就会返回False
        if form.is_valid():
            # 如果表单数据验证通过，我们通过访问form.cleaned_data获取验证过的数据。这个属性是一个表单字段和值的字典
            cd = form.cleaned_data
            # 将这个绝对路径作为request.build_absolute_uri()的输入值来构建一个完整的包含了HTTP schema和主机名的url
            post_url = request.build_absolute_uri(
                    # post.get_absolute_url()方法来获取到帖子的绝对路径
                    post.get_absolute_url())
            # 邮件主题
            subject = '{}({})recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            # 内容
            message = 'Read"{}"at{}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'maojiaxu@yeah.net', [cd['to']])
            sent = True
    else:
        # 通过GET请求视图（view）被初始加载后，我们创建一个新的表单实例，用来在模板（template）中显示一个空的表单：
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


def post_search(request):
    form = SearchForm()
    cd = None
    results = None
    total_results = None
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            results = SearchQuerySet.models(Post).filter(content=cd['query']).load_all()
            # count total results
            total_results = results.count()

    return render(request, 'blog/post/search.html',
                  {'form': form,
                   'cd': cd,
                   'results': results,
                   'total_results': total_results})
