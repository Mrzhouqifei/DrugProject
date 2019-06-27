import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import collections
import copy

def generate_word_count():
    def wordCount(text):
        word_list = []
        for word in text:
            if len(word) > 1:
                word_list.append(word)
        word_counts = collections.Counter(word_list)  # 对分词做词频统计
        word_counts_top10 = word_counts.most_common(20)  # 获取前20最高频的词
        word_count_res = []
        for x in word_counts_top10:
            word_count_res.append(x)
        return word_count_res

    def generateCloud(text, name):
        text = "".join(list(text['content']))
        text = re.sub("[A-Za-z0-9\!\%\[\]\,\。\？\:\.\@\，\！\/\“\”\…\：\、\；\：\）\（\(\)\《\》\?\～\—\ \回复\・]", "", text)
        text = list(jieba.cut(text))
        # word count
        word_count_res = wordCount(text)

        # 生成一个词云图像
        text = " ".join(text)
        # max_font_size设定生成词云中的文字最大大小
        # width,height,margin可以设置图片属性
        # generate 可以对全部文本进行自动分词,但是他对中文支持不好||
        font = 'SimHei.ttf'
        wordcloud = WordCloud(font_path=font, width=2000, height=1200, margin=0, collocations=False).generate(text) #
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        # plt.show()
        wordcloud.to_file('output/'+name + '.png')
        plt.close()
        return word_count_res

    comments = pd.read_csv('data/Comments_all.csv')

    comments['person'] = comments['weibo_url'].str.contains('2302663124')
    zhendong = comments[comments['person']]
    zhendong_all = zhendong[zhendong['created_at'] > '2014-8-5']
    zhendong_all.dropna(inplace=True)
    word_count_res_all = generateCloud(zhendong_all, 'zhendong_all')
    df_all = pd.DataFrame(word_count_res_all)
    df_all['year'] = 'all'

    zhendong_2014 = zhendong[(zhendong['created_at'] > '2014-8-5') & (zhendong['created_at'] < '2015-1-1')]
    zhendong_2014.dropna(inplace=True)
    word_count_res_2014 = generateCloud(zhendong_2014, 'zhendong_2014')
    df_2014 = pd.DataFrame(word_count_res_2014)
    df_2014['year'] = '2014'
    df_all = pd.concat((df_all, df_2014))

    zhendong_2015 = zhendong[(zhendong['created_at'] >= '2015-1-1')&(zhendong['created_at'] < '2016-1-1')]
    zhendong_2015.dropna(inplace=True)
    word_count_res_2015 = generateCloud(zhendong_2015, 'zhendong_2015')
    df_2015 = pd.DataFrame(word_count_res_2015)
    df_2015['year'] = '2015'
    df_all = pd.concat((df_all, df_2015))

    zhendong_2016 = zhendong[(zhendong['created_at'] >= '2016-1-1') & (zhendong['created_at'] < '2017-1-1')]
    zhendong_2016.dropna(inplace=True)
    word_count_res_2016 = generateCloud(zhendong_2016, 'zhendong_2016')
    df_2016 = pd.DataFrame(word_count_res_2016)
    df_2016['year'] = '2016'
    df_all = pd.concat((df_all, df_2016))

    zhendong_2017 = zhendong[(zhendong['created_at'] >= '2017-1-1') & (zhendong['created_at'] < '2018-1-1')]
    zhendong_2017.dropna(inplace=True)
    word_count_res_2017 = generateCloud(zhendong_2017, 'zhendong_2017')
    df_2017 = pd.DataFrame(word_count_res_2017)
    df_2017['year'] = '2017'
    df_all = pd.concat((df_all, df_2017))

    zhendong_2018 = zhendong[(zhendong['created_at'] >= '2018-1-1') & (zhendong['created_at'] < '2019-1-1')]
    zhendong_2018.dropna(inplace=True)
    word_count_res_2018 = generateCloud(zhendong_2018, 'zhendong_2018')
    df_2018 = pd.DataFrame(word_count_res_2018)
    df_2018['year'] = '2018'
    df_all = pd.concat((df_all, df_2018))

    df_all.to_csv('output/zhendong_res.csv')