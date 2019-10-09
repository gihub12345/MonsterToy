import jieba
import gensim
from gensim import corpora
from gensim import models
from gensim import similarities
from day9520190719.MonsterToy.setting import db


# 查询MongoDB中Content表中的所有歌曲
l1 = list(db.Content.find({}))

# 问题库分词结果
all_doc_list = []

# 遍历歌曲列表，创建分词库
for doc in l1:  # 遍历问题库
    doc_list = list(jieba.cut_for_search(doc.get("title")))
    all_doc_list.append(doc_list)

# 制作歌曲词袋
dictionary = corpora.Dictionary(all_doc_list)  # 制作词袋
# 创建相似度的分词列表
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
# 使用Lsi模型进行训练
lsi = models.LsiModel(corpus)
# 稀疏矩阵相似度 将 主 语料库corpus的训练结果 作为初始值
index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))


# 用户表达分词结果，获取用户信息
def my_nlp_content(Q):
    # jieba问题分词
    doc_test_list = list(jieba.cut_for_search(Q))
    # 创建相似度的分词列表
    doc_test_vec = dictionary.doc2bow(doc_test_list)
    # 稀疏矩阵相似度匹配
    sim = index[lsi[doc_test_vec]]
    # 匹配结果排序
    cc = sorted(enumerate(sim), key=lambda item: -item[1])
    # 相似度高于78%
    if cc[0][1] >= 0.68:
        text = l1[cc[0][0]]
        # print(text)
        # 返回最后匹配的歌曲名
        return text


