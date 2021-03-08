from __future__ import unicode_literals
import datetime
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template import loader
from myfirstvis.chart import *
from news_extract.spider import main
from . import forms
from . import models
import json


def default(request):
    return render(request, 'default.html', dict())


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
            except:
                message = '用户不存在！'
                return render(request, 'login/login.html', locals())

            if user.password == hash_code(password):
                request.session['is_login'] = True
                # request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['c_time'] = str(user.c_time)[0:10]
                request.session['user_email'] = user.email
                # request.session['user_sex'] = user.sex
                return redirect('/drug/analysis/')
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


def index(request):
    if not request.session.get('is_login', None):
        return redirect('/drug/login/')
    # all_news = models.News.objects.all()
    all_news = models.News.objects.only('news_title', 'news_url', 'news_date')

    data = pd.read_csv('data/regression.csv')
    x, y, y_pred = list(data.x), list(data.y), list(data.y_pred)
    regression1 = line_smooth(x, y, y_pred)
    return render(request, 'index.html', locals())


def analysis(request):
    date_range = request.POST.get('date_range', '')
    startdate = '2010-01-01'
    enddate = str(datetime.date.today())
    if len(date_range) > 0:
        startdate = date_range[6:10] + '-' + date_range[0:2] + '-' + date_range[3:5]
        enddate = date_range[6 + 22:10 + 22] + '-' + date_range[0 + 22:2 + 22] + '-' + date_range[3 + 22:5 + 22]
    print(startdate, enddate)

    # ---------------------theme begin-----------------------
    province = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽',
                '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃',
                '青海', '台湾', '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门']
    theme = models.News.objects.filter(news_date__gt=startdate,
                                       news_date__lte=enddate).values_list("news_theme", flat=True)
    theme_temp = pd.DataFrame(theme, columns=['num'])['num'].value_counts()
    themes = set(theme_temp.index).difference(set(province))
    theme_list = []
    theme_num = []
    for i, x in enumerate(theme_temp.index):
        if x in themes:
            theme_list.append(x)
            theme_num.append(theme_temp[i])
    theme_last = theme_list[0:12]
    theme_last.append('其他')
    num_last = theme_num[0:12]
    num_last.append(sum(theme_num[12:]))
    themepie = pie_(theme_last, num_last)
    # ---------------------theme end-------------------------

    # ---------------------action begin----------------------
    action_temp = models.News.objects.filter(news_date__gt=startdate,
                                             news_date__lte=enddate).values_list("news_action", flat=True)
    action_temp = pd.DataFrame(action_temp, columns=['num'])['num'].value_counts()
    action = list(action_temp.index)
    num = list(action_temp)
    action_dict = dict()
    for i in range(len(action)):
        xx = list(set(action[i].split(',')))
        for x in xx:
            if x == '':
                continue
            if x in action_dict:
                action_dict[x] += num[i]
            else:
                action_dict[x] = num[i]
    actionpie = pie_(list(action_dict.keys()), list(action_dict.values()))
    # ---------------------action end------------------------

    # ---------------------drug begin-----------------------
    drugs_temp = models.News.objects.filter(news_date__gt=startdate,
                                            news_date__lte=enddate).values_list("news_drug", flat=True)
    drugs_temp = pd.DataFrame(drugs_temp, columns=['num'])['num'].value_counts()
    drugs_temp = drugs_temp[drugs_temp.index != '']
    name = list(drugs_temp.index)  # [1:]
    num = list(drugs_temp)
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
    drugbar = bar_(list(drug_dict.keys()), list(drug_dict.values()))
    # -----------------------drug end--------------------------

    # -----------------------word begin------------------------
    word_temp = models.News.objects.filter(news_date__gt=startdate,  # news_title news_content
                                           news_date__lte=enddate).values_list("news_title", flat=True)
    wordcloud = wordcloud_diamond(wordCount(word_temp))
    # -----------------------word end--------------------------



    theme = models.News.objects.filter(news_date__gt=startdate,
                                       news_date__lte=enddate).values_list("news_theme", flat=True)
    province = models.News.objects.filter(news_date__gt=startdate,
                                          news_date__lte=enddate).values_list("news_province", flat=True)
    theme = pd.Series(theme)
    theme = list((theme == '缉毒破案') | (theme == '曝光台'))

    # -----------------------region1 begin------------------------
    res_all = []
    for i in range(len(province)):
        temp1 = province[i].split(',')
        for x in temp1:
            res_all.append(x)
    res_all = pd.DataFrame(res_all, columns=['num'])['num'].value_counts()
    res_all = res_all[res_all.index != '']
    res_name = list(res_all.index)
    num = list(res_all)
    region1 = map_(res_name, num)


    context = dict(
        drugbar=drugbar,
        themepie=themepie,
        actionpie=actionpie,
        wordcloud=wordcloud,
        region1=region1,
    )
    if len(date_range) > 0:
        response = JsonResponse({"status": '服务器接收成功', 'themepie': themepie, 'actionpie': actionpie,
                                 'drugbar': drugbar, 'wordcloud': wordcloud})
        return response
    return render(request, 'analysis.html', context)


def region(request):
    """
    毒品形势中国区域分布
    :param request:
    :return:
    """
    date_range = request.POST.get('date_range', '')
    startdate = '2010-01-01'
    enddate = str(datetime.date.today())
    if len(date_range) > 0:
        startdate = date_range[6:10] + '-' + date_range[0:2] + '-' + date_range[3:5]
        enddate = date_range[6 + 22:10 + 22] + '-' + date_range[0 + 22:2 + 22] + '-' + date_range[3 + 22:5 + 22]
    print(startdate, enddate)

    theme = models.News.objects.filter(news_date__gt=startdate,
                                       news_date__lte=enddate).values_list("news_theme", flat=True)
    province = models.News.objects.filter(news_date__gt=startdate,
                                          news_date__lte=enddate).values_list("news_province", flat=True)
    theme = pd.Series(theme)
    theme = list((theme == '缉毒破案') | (theme == '曝光台'))

    # -----------------------region1 begin------------------------
    # res_all = []
    # for i in range(len(province)):
    #     temp1 = province[i].split(',')
    #     for x in temp1:
    #         res_all.append(x)
    # res_all = pd.DataFrame(res_all, columns=['num'])['num'].value_counts()
    # res_all = res_all[res_all.index != '']
    # res_name = list(res_all.index)
    # num = list(res_all)
    # region1 = map_(res_name, num)
    #
    # # -----------------------region2 begin------------------------
    # res_all = []
    # for i in range(len(province)):
    #     if not theme[i]:
    #         temp1 = province[i].split(',')
    #         for x in temp1:
    #             res_all.append(x)
    # res_all = pd.DataFrame(res_all, columns=['num'])['num'].value_counts()
    # res_all = res_all[res_all.index != '']
    # res_name = list(res_all.index)
    # num = list(res_all)
    # region2 = map_(res_name, num)

    # -----------------------region3 begin------------------------
    res_all = []
    for i in range(len(province)):
        if theme[i]:
            temp1 = province[i].split(',')
            for x in temp1:
                res_all.append(x)
    res_all = pd.DataFrame(res_all, columns=['num'])['num'].value_counts()
    res_all = res_all[res_all.index != '']
    res_name = list(res_all.index)
    num = list(res_all)
    region3 = map_(res_name, num)

    context = dict(
        # region1=region1,
        # region2=region2,
        region3=region3,
    )
    if len(date_range) > 0:
        response = JsonResponse({"status": '服务器接收成功', 'region1': region1, 'region2': region2,
                                 'region3': region3})
        return response
    return render(request, 'region.html', context)


def evaluation(request):
    last_startdate, startdate, enddate = '2017-12-31', '2018-12-31', '2019-12-31'
    request_date = request.POST.get('date', '')
    if len(request_date) > 0:
        last_startdate, startdate, enddate = str(int(request_date[:4])-1)+'-12-31', request_date[:10], request_date[11:]
    date = models.News.objects.values_list("news_date", flat=True)
    date = pd.to_datetime(pd.Series(date))
    date = date.dt.strftime('%Y')
    date = sorted(list(set(date[date >= '2015'])), reverse=True)
    date_options = []
    for x in date[1:]:
        date_options.append(str(int(x)-1)+'-12-31~'+x+'-12-31')

    province_name = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽',
                     '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃',
                     '青海', '台湾', '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门']

    all_dict, action_dict, publicize_dict, last_action_dict, last_publicize_dict = dict(), dict(), dict(), dict(), dict()
    for x in province_name:
        all_dict[x], action_dict[x], publicize_dict[x], last_action_dict[x], last_publicize_dict[x] = 50, 50, 50, 50, 50

    theme = models.News.objects.filter(news_date__gt=startdate,
                                       news_date__lte=enddate).values_list("news_theme", flat=True)
    province = models.News.objects.filter(news_date__gt=startdate,
                                          news_date__lte=enddate).values_list("news_province", flat=True)
    last_theme = models.News.objects.filter(news_date__gt=last_startdate,
                                            news_date__lte=startdate).values_list("news_theme", flat=True)
    last_province = models.News.objects.filter(news_date__gt=last_startdate,
                                               news_date__lte=startdate).values_list("news_province", flat=True)

    theme = pd.Series(theme)
    action = np.array((theme == '缉毒破案') | (theme == '曝光台') | (theme == '戒毒工作') |
                      (theme == '社区康复') | (theme == '禁毒人物') | (theme == '深度追踪') | (theme == '深度报道'))

    last_theme = pd.Series(last_theme)
    last_action = np.array((last_theme == '缉毒破案') | (last_theme == '曝光台') | (last_theme == '戒毒工作') |
                           (last_theme == '社区康复') | (last_theme == '禁毒人物') | (last_theme == '深度追踪') |
                           (last_theme == '深度报道'))

    res_action = []
    res_publicize = []
    for i in range(len(province)):
        temp1 = province[i].split(',')
        if action[i]:
            for x in temp1:
                res_action.append(x)
        else:
            for x in temp1:
                res_publicize.append(x)
    res_action = pd.DataFrame(res_action, columns=['num'])['num'].value_counts()
    res_action = res_action[res_action.index != '']
    res_action = (rank(res_action) + 1) / 2
    for i in range(len(res_action)):
        action_dict[res_action.index[i]] = int(res_action.iloc[i] * 100)

    res_publicize = pd.DataFrame(res_publicize, columns=['num'])['num'].value_counts()
    res_publicize = res_publicize[res_publicize.index != '']
    res_publicize = (rank(res_publicize) + 1) / 2
    for i in range(len(res_publicize)):
        publicize_dict[res_publicize.index[i]] = int(res_publicize.iloc[i] * 100)
    # -------last--------
    las_res_action = []
    last_res_publicize = []
    for i in range(len(last_province)):
        temp1 = last_province[i].split(',')
        if last_action[i]:
            for x in temp1:
                las_res_action.append(x)
        else:
            for x in temp1:
                last_res_publicize.append(x)
    las_res_action = pd.DataFrame(las_res_action, columns=['num'])['num'].value_counts()
    las_res_action = las_res_action[las_res_action.index != '']
    las_res_action = (rank(las_res_action) + 1) / 2
    for i in range(len(las_res_action)):
        last_action_dict[las_res_action.index[i]] = int(las_res_action.iloc[i] * 100)

    last_res_publicize = pd.DataFrame(last_res_publicize, columns=['num'])['num'].value_counts()
    last_res_publicize = last_res_publicize[last_res_publicize.index != '']
    last_res_publicize = (rank(last_res_publicize) + 1) / 2
    for i in range(len(last_res_publicize)):
        last_publicize_dict[last_res_publicize.index[i]] = int(last_res_publicize.iloc[i] * 100)

    for x in all_dict.keys():
        all_dict[x] = int(
            0.3 * action_dict[x] + 0.3 * publicize_dict[x] + 0.2 * last_action_dict[x] + 0.2 * last_publicize_dict[x])
    all_dict = dict(sorted(all_dict.items(), key=lambda x: x[1], reverse=True))
    keys = list(all_dict.keys())

    ranks_list = []

    if len(request_date) > 0:
        for key in keys:
            dict_row = {}
            dict_row['key'] = key
            dict_row['action'] = action_dict[key]
            dict_row['publicize'] = publicize_dict[key]
            dict_row['last_action'] = last_action_dict[key]
            dict_row['last_publicize'] = last_publicize_dict[key]
            dict_row['all'] = all_dict[key]
            ranks_list.append(dict_row)
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        response.write(json.dumps({'rows': ranks_list, 'total': len(ranks_list)}))
        return response
    else:
        class Ranks(object):
            key = str()
            action = str()
            publicize = str()
            last_action = str()
            last_publicize = str()
            all = str()

        for key in keys:
            ranks = Ranks()
            ranks.key = key
            ranks.action = action_dict[key]
            ranks.publicize = publicize_dict[key]
            ranks.last_action = last_action_dict[key]
            ranks.last_publicize = last_publicize_dict[key]
            ranks.all = all_dict[key]
            ranks_list.append(ranks)
        context = dict(
            ranks_list=ranks_list,
            date_options=date_options,
        )
        return render(request, 'evaluation.html', context)


def sentiment(request):
    sentiment = pd.read_csv('data/sentiment.csv')
    sentiment.columns = ['content', 'num', 'year']
    sentiment['num'] = sentiment['num'].astype(float)
    positive = ['加油', '喜欢', '支持', '微笑']
    negitive = ['吸毒', '什么', '缉毒', '警察']
    year_list, positive_list, negitive_list = [], [], []
    wordcouts=[]
    for key, group in sentiment.groupby('year'):
        year_list.append(key)
        positive_num, negitive_num = 0, 0
        for x in positive:
            try:
                positive_num += group[group.content == x]['num'].iloc[0]
            except:
                pass
        for x in negitive:
            try:
                negitive_num += group[group.content == x]['num'].iloc[0]
            except:
                pass
        sum_num = positive_num + negitive_num
        positive_list.append(np.round(positive_num/sum_num, 2))
        negitive_list.append(np.round(negitive_num/sum_num, 2))

        wordcount_list = []
        for i in range(len(group)):
            wordcount_list.append((group.content.iloc[i], group.num.iloc[i]))
        wordcouts.append(wordcloud_diamond(wordcount_list))

    sentimentbar = bar2_(year_list, positive_list, negitive_list)

    sentiment = sentiment.groupby(['content']).sum()
    wordcount_list = []
    for i in range(len(sentiment)):
        wordcount_list.append((sentiment.index[i], sentiment.num.iloc[i]))
    wordcoutsall = wordcloud_diamond(wordcount_list)
    context = dict(
        wordcoutsall=wordcoutsall,
        sentimentbar=sentimentbar,
        wordcouts14=wordcouts[0],
        wordcouts15=wordcouts[1],
        wordcouts16=wordcouts[2],
        wordcouts17=wordcouts[3],
        wordcouts18=wordcouts[4],
        wordcouts19=wordcouts[5],
    )
    return render(request, 'sentiment.html', context)


def individual(request):
    age = request.POST.get('age')  # 年龄
    if age is None:
        return render(request, 'individual.html', dict())
    else:
        # 基础风险
        basic_risk = 0
        age = request.POST.get('age')   # 年龄
        nation = request.POST.get('nation')  # 民族
        gender = request.POST.get('gender')  # 性别
        education = request.POST.get('education')   # 教育
        marry = request.POST.get('marry')  # 结婚年龄
        profession = request.POST.get('profession')  # 职业大类
        smoke_age = request.POST.get('smoke_age')  # 首次吸烟年龄
        smoke_num = request.POST.get('smoke_num')  # 周吸烟量
        smoke_quit = request.POST.get('smoke_quit')  # 戒烟年龄
        drug_age = request.POST.get('drug_age')  # 成瘾药物首次使用年龄
        drug_num = request.POST.get('drug_num')  # 月使用次数
        alcohol_age = request.POST.get('alcohol_age')  # 首次酒精使用年龄
        alcohol_num = request.POST.get('alcohol_num')  # 30天内酒精使用数量
        alcohol_max = request.POST.get('alcohol_max')  # 24H饮酒上限(两)

        try:
            if int(age) > 15:
                basic_risk += 2
            if nation == '汉':
                basic_risk += 2
            if gender == '女':
                basic_risk += 2
            if education == '大专':
                basic_risk += 5
            if int(marry) < 20:
                basic_risk += 10
            if profession == '经济学':
                basic_risk += 5
            if -1 < int(smoke_age) < 20:
                basic_risk += 10

            if int(smoke_num) > 6:
                basic_risk += 10
            if int(smoke_quit) < 40:
                basic_risk = basic_risk // 2

            if int(drug_age) != -1:
                basic_risk += 30
            if int(drug_num) > 1:
                basic_risk += 30
            if int(alcohol_age) < 15:
                basic_risk += 10
            if int(alcohol_num) > 70:
                basic_risk += 10
            if int(alcohol_max) > 20:
                basic_risk += 10
        except:
            print(basic_risk)


        # ---------------------------------- 药物滥用主观程度
        drug_abuse = 0
        tianbao_kewang = request.POST.get('tianbao_kewang')  # 自我填报渴望程度
        life_satisfaction = request.POST.get('life_satisfaction')  # 目前生活满意度（1-5分）
        motivation = request.POST.get('motivation')  # 动机
        current_subjective = request.POST.get('current_subjective')  # 目前主观
        past_subjective = request.POST.get('past_subjective')  # 过去主观
        try:
            drug_abuse += int(tianbao_kewang)
            drug_abuse = drug_abuse + (5-int(life_satisfaction)) * 2
            if motivation == '无法控制':
                drug_abuse += 30
            if motivation == '爱好' or motivation == '攀比':
                drug_abuse += 10
            if current_subjective == '喜欢':
                drug_abuse += 10
            if current_subjective == '一般':
                drug_abuse += 5
            if past_subjective == '喜欢':
                drug_abuse += 8
            if past_subjective == '一般':
                drug_abuse += 2
        except:
            print(drug_abuse)
        drug_abuse = int(drug_abuse * 1.5)

        # --------------------------------药物滥用相关复发病和健康量表
        relapse = 0
        aids = request.POST.get('aids')
        abstinence = request.POST.get('abstinence')  # 禁欲时常（天）
        medical = request.POST.get('medical')
        treatment = request.POST.get('treatment')
        health_index = request.POST.get('health_index')  # 经济角度评估的健康质量指数
        behavioral_health = request.POST.get('behavioral_health')  # 行为健康筛查

        try:
            relapse += 4 * int(aids)
            if int(abstinence) < 2:
                relapse += 5
            if medical == '中':
                relapse += 2
            if medical == '差':
                relapse += 5
            if treatment == '中':
                relapse += 2
            if treatment == '差':
                relapse += 5
            if health_index == '中':
                relapse += 2
            if health_index == '差':
                relapse += 5
            if behavioral_health == '中':
                relapse += 2
            if behavioral_health == '差':
                relapse += 5
        except:
            print(relapse)

        relapse = relapse * 2

        # -------------------------神经行为学
        neurobehavioral = 0
        cognitive_flexibility = request.POST.get('cognitive_flexibility')  # 认知灵活性
        decision_capacity = request.POST.get('decision_capacity')  # 决策能力
        delay_reward = request.POST.get('delay_reward')  # 延迟奖励
        behavioral_inhibition = request.POST.get('behavioral_inhibition')  # 行为抑制控制
        risk_possibility = request.POST.get('risk_possibility')  # 冒险可能性测试
        extreme_behavior = request.POST.get('extreme_behavior')  # 极端行为可能性
        punishment = request.POST.get('punishment')  # 对奖惩制度敏感性
        try:
            neurobehavioral += (5 - int(cognitive_flexibility))
            neurobehavioral += (5 - int(decision_capacity))
            neurobehavioral += (5 - int(delay_reward))
            neurobehavioral += (5 - int(behavioral_inhibition))
            neurobehavioral += int(risk_possibility)
            neurobehavioral += int(extreme_behavior) * 2
            neurobehavioral += (5 - int(punishment))
        except:
            print(neurobehavioral)
        neurobehavioral = neurobehavioral * 2

        # -------------------------社会及遗传学
        genetic = 0
        family_history = request.POST.get('family_history')  # 是否有家庭药物滥用历史
        partner_drug = request.POST.get('partner_drug')  # 伴侣是否使用成瘾药品
        community_risk = request.POST.get('community_risk')  # 社区风险
        family_risk = request.POST.get('family_risk')  # 家庭风险
        school_risk = request.POST.get('school_risk')  # 学校风险
        genetic_risk = request.POST.get('genetic_risk')  # 基因成瘾风险
        try:
            if family_history == '是':
                genetic += 30
            if partner_drug == '是':
                genetic += 40
            genetic += int(community_risk)
            genetic += int(family_risk) * 4
            genetic += int(school_risk)
            genetic += int(genetic_risk) * 3
        except:
            print(genetic)
        genetic = min(99, genetic)

        individual_radar = radar_([[basic_risk, drug_abuse, relapse, neurobehavioral, genetic]])
        context = dict(
            individual_radar=individual_radar,
        )
        if basic_risk != 0:
            response = JsonResponse({"status": '服务器接收成功', 'individual_radar': individual_radar})
            return response
        return render(request, 'individual.html', context)
