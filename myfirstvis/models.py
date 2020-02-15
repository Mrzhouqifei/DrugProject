from django.db import models

# Create your models here.
class User(models.Model):

    gender = (
        ('male', "男"),
        ('female', "女"),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default="男")
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"


class News(models.Model):
    news_title = models.CharField(max_length=256)
    news_url = models.CharField(max_length=256)
    news_date = models.DateField(null=True, blank=True, verbose_name="发布日期")

    class Meta:
        ordering = ["-news_date"]
        verbose_name = '涉毒新闻表'
        verbose_name_plural = "涉毒新闻表"
