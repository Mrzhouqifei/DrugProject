import urllib.request
import re
import pandas as pd
from bs4 import BeautifulSoup

def extract(urls, sel_year):
    '''
    :param urls:
    :return: res_single 每个新闻分别为一条记录, res_sum 所有新闻汇总记录
    '''
    res = dict()
    res_single = []

    # 市--省对应表构建
    city_prov = dict()
    citys = pd.read_excel('data/区县级行政区划清单 V20.0.xlsx')
    citys.columns = ['province', 'city']
    citys.drop_duplicates(inplace=True)
    citys.reset_index(drop=True, inplace=True)
    citys = citys[citys.province != citys.city]
    citys.province = citys.province.str.replace('市|省|自治区|特别行政区|维吾尔|回族|壮族', '')
    citys.city = citys.city.str.replace('市|县', '')
    for i in range(len(citys)):
        city_prov[citys.city.iloc[i]] = citys.province.iloc[i]

    # 新闻url
    news_urls = []
    # 毒品名称
    drug_name = ['彩虹烟', '笑气', '蓝精灵', '咔哇潮饮', '紫水', '海洛因', '大麻', '可卡因', '冰毒', 'k粉',
                 '吗啡', '摇头丸', '麻谷丸', '鸦片']
    drug_name_par = re.compile('彩虹烟|笑气|蓝精灵|咔哇潮饮|紫水|海洛因|大麻|可卡因|冰毒|k粉|吗啡|摇头丸|麻谷丸|鸦片')
    # 毒品类型
    drug_type = ['第三代毒品', '第一代毒品', '第二代毒品']
    drug_type_par = re.compile('三[代级]毒品|一[代级]毒品|二[代级]毒品')
    # 地点（省份），只有吉林省市同名
    drug_location = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽',
                     '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃',
                     '青海', '台湾', '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门']
    # 时间（年份）
    year_pat = re.compile('\d{4}[-年]')

    print('去重前', len(urls))
    urls = list(set(urls))
    print('去重后', len(urls))
    for url in urls:
        res_temp = dict()
        # 该网址的源码(以该网页的原编码方式进行编码，特殊字符编译不能编码就设置ignore)
        try:
            source = urllib.request.urlopen(url).read()
            source = source.decode("utf-8", "ignore") + source.decode("gbk", "ignore")
            # webSourceCode = re.sub('<a(.|\n)*</a>|(href)[^>]*>|pgcInfo[^\]]*]', '', source)
            # pat = re.compile('[\u4e00-\u9fa5]')
            # s = pat.findall(webSourceCode)
            # s = ''.join(s)
            # 中国禁毒网，用一下格式
            webSourceCode = re.sub('".*"','',source)
            s = webSourceCode.lower().strip()

            year = year_pat.findall(webSourceCode)
            if len(year) > 0:
                year = int(year[0][:4])
                if (sel_year != 0) and (year != sel_year):
                    continue
                res_temp['时间'] = year
                if year not in res:
                    res[year] = 1
                else:
                    res[year] += 1

            name = drug_name_par.findall(s)
            if len(name) > 0:
                name = name[0]
                res_temp['毒品名称'] = name
                if name not in res:
                    res[name] = 1
                else:
                    res[name] += 1

            types = drug_type_par.findall(s)
            if len(types) > 0:
                types = types[0]
                res_temp['毒品类型'] = types
                if types not in res:
                    res[types] = 1
                else:
                    res[types] += 1

            # 市转换成省
            for city in city_prov:
                if city in s:
                    s = s + city_prov[city]

            temp = []
            for location in drug_location:
                if location in s:
                    temp.append(location)
                    if location not in res:
                        res[location] = 1
                    else:
                        res[location] += 1
                if len(temp) > 0:
                    res_temp['涉毒地区'] = temp
            res_single.append(res_temp)
        except:
            print('url is not valid!')

    #区域统计
    region = dict()
    for key in res:
        if key in drug_location:
            region[key] = res[key]
    region = pd.DataFrame.from_dict(region, orient='index')
    region['city'] = region.index
    region.columns = ['num', 'city']
    region.to_csv('data/region.csv', index=False)

    #毒品类型统计
    drugs = dict()
    for key in res:
        if key in drug_name:
            drugs[key] = res[key]
    drugs = pd.DataFrame.from_dict(drugs, orient='index')
    drugs['drug'] = drugs.index
    drugs.columns = ['num', 'drug']
    drugs.to_csv('data/drugs.csv', index=False)

    return res, res_single

