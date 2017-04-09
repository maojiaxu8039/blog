from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from taggit.managers import TaggableManager

"""
objects是每一个模型（models）的默认管理器（manager），它会返回数据库中所有的对象。
但是我们也可以为我们的模型（models）定义一些定制的管理器（manager）。我们准备创建一个定制的管理器（manager）来返回所有状态为已发布的帖子。
"""


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


# Create your models here.
class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('Published', 'Published'),
    )
    # title： 这个字段对应帖子的标题。它是CharField，在SQL数据库中会被转化成VARCHAR。
    title = models.CharField(max_length=250)
    # slug：这个字段将会在URLs中使用。slug就是一个短标签，该标签只包含字母，数字，下划线或连接线。我们将通过使用slug字段给我们的blog帖子构建漂亮的，友好的URLs。我们给该字段添加了unique_for_date参数，这样我们就可以使用日期和帖子的slug来为所有帖子构建URLs。在相同的日期中Django会阻止多篇帖子拥有相同的slug。
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    # author：这是一个ForeignKey。这个字段定义了一个多对一（many-to-one）的关系。我们告诉Django一篇帖子只能由一名用户编写，一名用户能编写多篇帖子。根据这个字段，Django将会在数据库中通过有关联的模型（model）主键来创建一个外键。在这个场景中，我们关联上了Django权限系统的User模型（model）。我们通过related_name属性指定了从User到Post的反向关系名。
    author = models.ForeignKey(User, related_name='blog_posts')
    # body：这是帖子的主体。它是TextField，在SQL数据库中被转化成TEXT。
    body = models.TextField()
    # publish：这个日期表明帖子什么时间发布。我们使用Djnago的timezone的now方法来设定默认值
    publish = models.DateTimeField(default=timezone.now)
    # created：这个日期表明帖子什么时间创建。因为我们在这儿使用了auto_now_add，当一个对象被创建的时候这个字段会自动保存当前日期。
    created = models.DateTimeField(auto_now_add=True)
    # updated：这个日期表明帖子什么时候更新。因为我们在这儿使用了auto_now，当我们更新保存一个对象的时候这个字段将会自动更新到当前日期
    updated = models.DateTimeField(auto_now=True)
    # status：这个字段表示当前帖子的展示状态。我们使用了一个choices参数，这样这个字段的值只能是给予的选择参数中的某一个值。（译者注：传入元组，比如(1,2)，那么该字段只能选择1或者2，没有其他值可以选择）
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    objects = models.Manager()
    # 继承创建的PublishedManager管理器
    published = PublishedManager()

    """
    你可以使用之前定义的post_detail URL给Post对象构建标准URL。
    Django的惯例是给模型（model）添加get_absolute_url()方法用来返回一个对象的标准URL。
    在这个方法中，我们使用reverse()方法允许你通过它们的名字和可选的参数来构建URLS。编辑你的models.py文件添加如下代码：
    """

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.strftime('%m'),
                             self.publish.strftime('%d'),
                             self.slug])

    # 给Post模型（model）添加django-taggit提供的TaggableManager管理器（manager）
    tags = TaggableManager()

    # 在模型（model）中的类Meta包含元数据。我们告诉Django查询数据库的时候默认返回的是根据publish字段进行降序排列过的结果。我们使用负号来指定进行降序排列。
    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    # related_name属性允许我们给这个属性命名，这样我们就可以利用这个关系从相关联的对象反向定位到这个对象
    post = models.ForeignKey(Post, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on{}'.format(self.name, self.post)
