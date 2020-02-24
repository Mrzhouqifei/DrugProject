from pyecharts.charts import Geo, Map, Bar, Pie, Line
from pyecharts.globals import ThemeType
from pyecharts import options as opts
import collections
import jieba
from pyecharts.charts import Page, WordCloud
from pyecharts.globals import SymbolType
import hashlib
import numpy as np



def rank(df):
    """
    Cross sectional rank
    :param df: a pandas DataFrame.
    :return: a pandas DataFrame with rank along columns.
    """
    return df.rank(axis=0, pct=True)


def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


def wordCount(text):
    text = "".join(list(text))
    text = list(jieba.cut(text))
    word_list = []
    for word in text:
        if len(word) > 1 and (word != '...'):
            word_list.append(word)
    word_counts = collections.Counter(word_list)  # 对分词做词频统计
    word_counts_top = word_counts.most_common(100)  # 获取前20最高频的词
    word_count_res = []
    for x in word_counts_top:
        word_count_res.append(x)
    return word_count_res


def wordcloud_diamond(words):
    c = (
        WordCloud(init_opts=opts.InitOpts(width="560px", height="400px"))
        .add("", words, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
        # .set_global_opts(title_opts=opts.TitleOpts(title="WordCloud-shape-diamond"))
        .set_global_opts(  # title_opts=opts.TitleOpts(title='毒品报道情况统计'),
            toolbox_opts=opts.ToolboxOpts(),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=0)), )
    )
    return c.render_embed()


def bar_(x, y):
    bar = (
        Bar(init_opts=opts.InitOpts(width="560px", height="400px"))# theme=ThemeType.CHALK
            .add_xaxis(x)
            .add_yaxis('数量', y)
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
    return bar.render_embed()


def pie_(x, y):
    pie_in = []
    for i in range(len(x)):
        pie_in.append((x[i], int(y[i])))
    c = (
        Pie(init_opts=opts.InitOpts(width="560px", height="400px"))
        .add(
            "",
            pie_in,
            radius=["40%", "75%"],
        )
        .set_global_opts(
            toolbox_opts=opts.ToolboxOpts(),
            legend_opts=opts.LegendOpts(
                is_show=False,# orient="vertical", pos_top="15%", pos_left="2%"
            ),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c.render_embed()


def map_(x, y):
    max_count = np.mean(y) + 3 * np.std(y)
    #[("海门", 9), ("鄂尔多斯", 12), ("大庆", 279)]
    cmap = (
        Map(init_opts=opts.InitOpts(width="1100px", height="550px"))#, theme=ThemeType.CHALK
        .add('统计数目', [list(z) for z in zip(x, y)], maptype="china", is_roam=False, zoom=1.2)#"",, "china"
        .set_global_opts(
            # title_opts=opts.TitleOpts(subtitle='数据主要来源于:中国禁毒网|禁毒在线|新浪新闻'),#title="中国毒情区域分布",
            visualmap_opts=opts.VisualMapOpts(max_=max_count),#max_=max_count, textstyle_opts=opts.TextStyleOpts(color='#fff')
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return cmap.render_embed()


def line_smooth(x, y, y_pred):
    c = (
        Line(init_opts=opts.InitOpts(width="1100px", height="300px"))
        .add_xaxis(x)
        .add_yaxis("历史变化", y, is_smooth=True)
        .add_yaxis("未来预测", y_pred, is_smooth=True)
        .set_global_opts( title_opts=opts.TitleOpts(title='毒品报道统计及预测'),
            toolbox_opts=opts.ToolboxOpts(),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=0)), )
    )
    return c.render_embed()