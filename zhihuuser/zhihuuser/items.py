from scrapy import Item, Field


class UserItem(Item):
    # define the fields for your item here like:
    collection = 'User'
    id = Field()
    name = Field()                      #用户昵称
    avatar_url = Field()                #头像URl
    headline = Field()                  #个人主页的标签
    description = Field()               #个人描述
    url = Field()
    url_token = Field()                 #知乎给予的每个人用户主页唯一的ID
    gender = Field()
    cover_url = Field()
    type = Field()
    badge = Field()

    answer_count = Field()              #回答数量
    articles_count = Field()            #写过的文章数
    commercial_question_count = Field()
    favorite_count = Field()
    favorited_count = Field()           #被收藏次数
    follower_count = Field()            #粉丝数量
    following_columns_count = Field()
    following_count = Field()           #关注了多少人
    pins_count = Field()
    question_count = Field()
    thank_from_count = Field()
    thank_to_count = Field()
    thanked_count = Field()             #获得的感谢数
    vote_from_count = Field()
    vote_to_count = Field()
    voteup_count = Field()              #获得的赞数
    following_favlists_count = Field()
    following_question_count = Field()
    following_topic_count = Field()
    marked_answers_count = Field()
    mutual_followees_count = Field()
    hosted_live_count = Field()
    participated_live_count = Field()

    locations = Field()                 #所在地
    educations = Field()                #教育背景
    employments = Field()               #工作信息