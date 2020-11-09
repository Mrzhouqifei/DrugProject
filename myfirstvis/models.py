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
        verbose_name = "用户表"
        verbose_name_plural = "用户表"


class News(models.Model):
    """
    标题，主题，内容，毒品，省，市，县，网址，日期
    province, city, county
    """
    news_title = models.CharField(max_length=128)
    news_theme = models.CharField(max_length=128, default=' ')
    news_content = models.CharField(max_length=512, default=' ')
    news_drug = models.CharField(max_length=64, default=' ')
    news_province = models.CharField(max_length=64, default=' ')
    news_city = models.CharField(max_length=64, default=' ')
    news_county = models.CharField(max_length=64, default=' ')
    news_url = models.CharField(max_length=128)
    news_date = models.DateField(max_length=64)
    news_action = models.CharField(max_length=64, default=' ')

    class Meta:
        ordering = ["-news_date"]
        verbose_name = '涉毒新闻表'
        verbose_name_plural = "涉毒新闻表"
