import jieba
import gensim
from gensim import corpora
from gensim import models
from gensim import similarities

l1 = ["你的名字是什么", "你今年几岁了", "你有多高你胸多大", "你胸多大"]
a = "你今年多大了"

all_doc_list = []
for doc in l1:
    doc_list = [word for word in jieba.cut(doc)]
    all_doc_list.append(doc_list)

print(all_doc_list)
doc_test_list = [word for word in jieba.cut(a)]
print(doc_test_list)

# 制作语料库
dictionary = corpora.Dictionary(all_doc_list)  # 制作词袋
print(dictionary)

# 将需要寻找相似度的分词列表 做成 语料库 doc_test_vec
doc_test_vec = dictionary.doc2bow(doc_test_list)
print("doc_test_vec", doc_test_vec, type(doc_test_vec))

corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
print("corpus", corpus, type(corpus))

# 将corpus语料库(初识语料库) 使用Lsi模型进行训练
lsi = models.LsiModel(corpus)
# 这里的只是需要学习Lsi模型来了解的,这里不做阐述
print("lsi", lsi, type(lsi))
# 语料库corpus的训练结果
print("lsi[corpus]", lsi[corpus])
# 获得语料库doc_test_vec 在 语料库corpus的训练结果 中的 向量表示
print("lsi[doc_test_vec]", lsi[doc_test_vec])
