from __future__ import unicode_literals
import pandas as pd
import re
from django.http import HttpResponse, JsonResponse
from django.template import loader
from pyecharts.charts import Geo, Map, Bar
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from news_extract.news_extract import extract
from sentiment_classify.classify import predict
import numpy as np
from django.shortcuts import render
from django.shortcuts import redirect
from . import models
from . import forms
import hashlib
from news_extract.spider import main
import datetime
import json

def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()

# REMOTE_HOST = "https://pyecharts.github.io/assets/js"


def region(request):
    """
    毒品形势中国区域分布
    :param request:
    :return:
    """
    template = loader.get_template('region.html')
    region = pd.read_csv('data/region.csv')
    max_count = np.mean(region.num) + 3 * np.std(region.num)
    #[("海门", 9), ("鄂尔多斯", 12), ("大庆", 279)]
    cmap = (
        Map(init_opts=opts.InitOpts(width="1100px", height="550px", theme=ThemeType.CHALK))
        .add("涉毒数目", [list(z) for z in zip(list(region.city), list(region.num))], "china")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="中国毒情区域分布", subtitle='数据主要来源于:中国禁毒网|禁毒在线|新浪新闻'),
            visualmap_opts=opts.VisualMapOpts(max_=max_count, textstyle_opts=opts.TextStyleOpts(color='#fff')),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )

    drugs = pd.read_csv('data/drugs.csv')
    bar = (
        Bar(init_opts=opts.InitOpts(width="700px", height="350px", theme=ThemeType.CHALK))
        .add_xaxis(list(drugs.drug))
        .add_yaxis('数量', list(drugs.num))
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=True),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title='毒品报道情况统计'),
                         toolbox_opts=opts.ToolboxOpts(),
                         xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=0)),)
    )

    context = dict(
        mymap=cmap.render_embed(),
        mybar=bar.render_embed(),
    )
    return HttpResponse(template.render(context, request))


def news(request):
    """
    毒品形势中国区域分布
    :param request:
    :return:
    """
    template = loader.get_template('news.html')
    context = dict()
    if request.method == 'POST':
        if request.POST:
            urls = request.POST.get('urls', '').split()
            sel_year = int(request.POST.get('sel_year', ''))
            news_sum, news_items = extract(urls, sel_year)
            single_res = []
            for news_item in news_items:
                news_item = str(news_item)
                news_item = re.sub('[{}\'[\]]', '', news_item)
                single_res.append(news_item)
            context['news_items'] = single_res

            news_sum = str(news_sum)
            news_sum = re.sub('[{}\']', '', news_sum)
            news_sum = news_sum.replace(',', '\n')
            context['news_sum'] = news_sum
    return HttpResponse(template.render(context, request))


def sentiment(request):
    template = loader.get_template('sentiment.html')
    context = dict()
    if request.method == 'POST':
        if request.POST:
            raw = request.POST.get('comments', '')
            comments = raw.split()
            res = predict(comments)
            display = ''
            for x in res:
                if x == 1:
                    display += '接纳吸毒\n'
                else:
                    display += '抵制吸毒\n'
            context['display'] = display
            context['comments'] = raw
    return HttpResponse(template.render(context, request))


def demo(request):
    template = loader.get_template('demo.html')
    zhendong = pd.read_csv('data/zhendong_res.csv')[['0', '1', 'year']]

    zhendong14 = zhendong[zhendong['year'] == '2014'].drop(['year'], axis=1)
    zhendong14 = zhendong14.reset_index(drop=True)
    zhendong14.columns = [['关键词', '词频']]

    zhendong15 = zhendong[zhendong['year'] == '2015'].drop(['year'], axis=1)
    zhendong15 = zhendong15.reset_index(drop=True)
    zhendong15.columns = [['关键词', '词频']]

    zhendong16 = zhendong[zhendong['year'] == '2016'].drop(['year'], axis=1)
    zhendong16 = zhendong16.reset_index(drop=True)
    zhendong16.columns = [['关键词', '词频']]

    zhendong17 = zhendong[zhendong['year'] == '2017'].drop(['year'], axis=1)
    zhendong17 = zhendong17.reset_index(drop=True)
    zhendong17.columns = [['关键词', '词频']]

    zhendong18 = zhendong[zhendong['year'] == '2018'].drop(['year'], axis=1)
    zhendong18 = zhendong18.reset_index(drop=True)
    zhendong18.columns = [['关键词', '词频']]

    context = dict()
    context['zhendong14'] = zhendong14
    context['zhendong15'] = zhendong15
    context['zhendong16'] = zhendong16
    context['zhendong17'] = zhendong17
    context['zhendong18'] = zhendong18
    return HttpResponse(template.render(context, request))

def index(request):
    if not request.session.get('is_login', None):
        return redirect('/drug/login/')
    all_news = models.News.objects.all()
    return render(request, 'index.html', locals())

def analysis(request):
    date_range = request.POST.get('date_range', '')

    # theme = models.News.objects.values_list("news_theme", flat=True)
    # theme_frame = pd.DataFrame(theme)
    # theme_frame.to_csv('data/theme.csv')
    # print(set(theme))

    startdate = '2010-01-01'
    enddate = str(datetime.date.today())
    if len(date_range) > 0:
        startdate = date_range[6:10] + '-' + date_range[0:2] + '-' + date_range[3:5]
        enddate = date_range[6 + 22:10 + 22] + '-' + date_range[0 + 22:2 + 22] + '-' + date_range[3 + 22:5 + 22]
    print(startdate, enddate)
    drugs_temp = models.News.objects.filter(news_date__gt=startdate,
                                            news_date__lte=enddate).values_list("news_drug", flat=True)
    drugs_temp = pd.DataFrame(drugs_temp, columns=['num'])['num'].value_counts()
    name = list(drugs_temp.index[1:])
    num = list(drugs_temp[1:])
    drug_dict = dict()
    for i in range(len(name)):
        xx = list(set(name[i].split(',')))
        for x in xx:
            if x == '各种毒品':
                x = '各类毒品'
            if x in drug_dict:
                drug_dict[x] += num[i]
            else:
                drug_dict[x] = num[i]
    # print(drug_dict)

    bar = (
        Bar(init_opts=opts.InitOpts(width="500px", height="400px"))# theme=ThemeType.CHALK
            .add_xaxis(list(drug_dict.keys()))
            .add_yaxis('数量', list(drug_dict.values()))
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=True),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
            .set_global_opts(#title_opts=opts.TitleOpts(title='毒品报道情况统计'),
                             toolbox_opts=opts.ToolboxOpts(),
                             xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=0)), )
    )
    context = dict(
        drugbar=bar.render_embed(),
    )
    if len(date_range) > 0:
        response = JsonResponse({"status": '服务器接收成功', 'drugbar': bar.render_embed(),})
        return response
    return render(request, 'analysis.html', context)
    # return HttpResponse(template.render(context, request))


def login(request):
    if request.session.get('is_login', None):  # 不允许重复登录
        return redirect('/drug/index/')
    if request.method == 'POST':
        login_form = forms.UserForm(request.POST)
        message = '请检查填写的内容！'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            try:
                user = models.User.objects.get(name=username)
            except :
                message = '用户不存在！'
                return render(request, 'login/login.html', locals())

            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['c_time'] = str(user.c_time)[0:10]
                return redirect('/drug/index/')
            else:
                message = '密码不正确！'
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/drug/index/')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')

            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册了！'
                    return render(request, 'login/register.html', locals())

                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                return redirect('/drug/login/')
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/drug/login/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/drug/login/")

def crawlNews(request):
    from threading import Thread
    try:
        print('爬取新数据')
        t = Thread(target=main)
        t.start()
    except:
        print('网站反爬更新！请修改爬虫！')
    return redirect('/drug/index/')