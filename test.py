# from news_extract.news_extract import extract
# from sentiment_classify.classify import predict
# from word_cloud.word_cloud import generate_word_count
#
#
# # urls = [
# #     # "https://www.toutiao.com/a6687797349990793742/?tt_from=weixin&utm_campaign=client_share&wxshare_count=1&timestamp=1557134349&app=news_article&utm_source=weixin&utm_medium=toutiao_ios&req_id=201905061719080100290571687785A05&group_id=6687797349990793742",
# #     #    "http://hunan.ifeng.com/a/20180624/6676069_0.shtml",
# #         'http://www.jindu626.com/dfpd/js/8421.html']
# # comments = ['吸毒加油！',
# #             '不可原谅！',
# #             '回复@话题投稿君:本人并不是柯震东的粉，但是我还是想发声。吸毒咋了？跟我有什么关系吗，柯震东演技就是好我就爱看他拍的电影，他吸毒不会影响我看电影。谢谢',
# #             '回复@贪字营_陈先生家的猫:什么叫白死了，这不是知错改错了吗，缉毒警察贡献很大，作用也很大，取得的成果也很好，现在就只说我们眼前的柯震东不就是知错改错了吗，如果说像你们那些别人犯了错就不可原谅，那么谁还有信心改错，如果吸毒的人都无法得到原谅，那么就有越来越少的人去改错，牺牲的缉毒警察就越来越多，懂吗',
# #             '一起抵制吸毒艺人！[微笑]不能让缉毒警察白白牺牲[蜡烛][蜡烛][蜡烛]',
# #             '新的一年凯凯要开心[兔子]抛掉所有烦恼你还是我眼中那个大男孩你在我心中是最美[心]']
# # print(extract(urls))
# # print(predict(comments))
#
# # generate_word_count()
# import pandas as pd
# import os
# # path = os.getcwd()
#
# area = pd.read_excel('data/全国省市区县行政区划明细及人口(2018最全版).xls').iloc[:, 1:4]
# area.columns = ['province', 'city', 'county']
# province = set(area.province.str.replace('县|区|市|省|自治区|特别行政区|维吾尔|回族|壮族', ''))
# city = set(area.city.str.replace('县|区|市|省|自治区|特别行政区|维吾尔|回族|壮族', ''))
# county = set(area.county.str.replace('县|区|市|省|自治区|特别行政区|维吾尔|回族|壮族', ''))
#
# print(province)
# print(city)
# print(county)
# # citys = citys[citys.province != citys.city]
# # citys.province = citys.province.str.replace('县｜区｜市|省|自治区|特别行政区|维吾尔|回族|壮族', '')
# # citys.city = citys.city.str.replace('市|县｜区', '')
# # for i in range(len(citys)):
# #     city_prov[citys.city.iloc[i]] = citys.province.iloc[i]

# python manage.py runserver 0.0.0.0:8000


