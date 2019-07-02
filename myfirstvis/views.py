from __future__ import unicode_literals
import pandas as pd
import re
from django.http import HttpResponse
from django.template import loader
from pyecharts import Geo, Map, Bar
from news_extract.news_extract import extract
from sentiment_classify.classify import predict
import numpy as np

REMOTE_HOST = "https://pyecharts.github.io/assets/js"


def region(request):
    """
    毒品形势中国区域分布
    :param request:
    :return:
    """
    template = loader.get_template('region.html')
    data = []
    region = pd.read_csv('data/region.csv')
    for i in range(len(region)):
        temp = (region.city[i], region.num[i])
        data.append(temp)
    # data = [("海门", 9), ("鄂尔多斯", 12), ("大庆", 279)]
    temp = np.array(data)
    max_count = np.mean(temp[:,1].astype(int)) + 3 * np.std(temp[:,1].astype(int))
    map = Map("中国毒情区域分布", "（数据主要来源于中国禁毒网|禁毒在线|头条等媒体)", title_color="#fff", title_pos="center",
              width=1100, height=550, background_color='#404a59')
    attr, value = map.cast(data)
    map.add(
        "",
        attr,
        value,
        visual_range=[0, max_count],
        visual_text_color="#fff",
        symbol_size=15,
        is_visualmap=True,
        # is_piecewise=True,
        # visual_split_number=6,
    )
    data = []
    drugs = pd.read_csv('data/drugs.csv')
    for i in range(len(drugs)):
        temp = (drugs.drug[i], drugs.num[i])
        data.append(temp)
    attr, value = map.cast(data)
    bar = Bar("毒品报道情况统计", background_color='rgba(253,251,239,0.73)', width=700, height=350)
    bar.add("", attr, value, is_stack=True, xaxis_interval=0, is_label_show=True, mark_line=["average"])

    context = dict(
        mymap=map.render_embed(),
        mybar=bar.render_embed(),
        host=REMOTE_HOST,
        script_list=map.get_js_dependencies()
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