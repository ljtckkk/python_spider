url = 'https://www.zhihu.com/members/li-zhe-ao/followees?include=data%5B%2A%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=20&offset=20https://www.zhihu.com/members/url_token/followees?include=data%5B%2A%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=20&offset=20'

f = url.split('com/')
print(f)

full_url = f[0] + 'com/api/v4/' + f[1]
print(full_url)