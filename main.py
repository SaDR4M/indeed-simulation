from elasticsearch import Elasticsearch

client = Elasticsearch("http://127.0.0.1:9200/" , basic_auth=("elastic" , "13832004"))

mappings = {
    "properties" : {
            "title" : {"type" : "keyword"},
            "price" : {"type" : "integer"},
            "category" : {"type" : "text"},    
            "added_at" : {"type" : "date"}        
    } 
}

client.indices.delete(index = "my_index")
# client.indices.create(index="my_index" , mappings=mappings)
# doc_1 = client.index(index="my_index" , document={"title" : "lotr" , "price" : 25000 , "category" : "book"})
# doc_2 = client.index(index="my_index" , document={"title" : "harry potter" , "price" : 50000 , "category" : "book"})
# doc_3 = client.index(index="my_index" , document={"title" : "boot" , "price" : 100000 , "category" : "shoe"})
# s_1 = client.search(index="my_index" , aggregations={
#     "my_first_aggregation" : {
#         "avg" : {
#             "field" : "price"
#         }
#     }
# })
# print(s_1)
# s_2 = client.search(index="my_index" , aggregations={
#     "my_second_aggregation" : {
#         "terms" : {
#             "field" : "title"
#         }
#     }
# })
# print(s_2)
# s_3 = client.search(index="my_index" , aggregations={
#     "my_third_aggregation" : {
#         "range" : {
#             "field" : "price",
#             "ranges" : [ 
#              { "from" : 20000 , "to" : 80000}               
#             ]         
#         }
#     }
# })
# print(s_3)
# doc = client.search(index="my_index" , query={ 
#         "term" : {
#             "name" : "Sadra"
#         }
#       }
# )
# print(doc)


# doc_2 = client.search(index="my_index" , query={
#     "match" : {
#         "name" : "sadra"
#     }
# })
# print(doc_2)

# doc_3 = client.search(index="my_index" , query={
#     "range" : {
#         "age" : {
#             "gte" : 18,
#             "lte" : 21
#         }
#     }
# })
# print(doc_3)

# doc_4 = client.search(index="my_index" , query={
#     "match" : {
#         "about" : {"query" : "django developer" , "operator" : "and"}
#     }
# })
# print(doc_4)
# doc_5 = client.search(index="my_index" , query={
#     "bool" : {
#         "must" : [
#             {"match" : {
#                 "about" : {
#                     "query" : "django developer",
#                     "operator" : "or"
#                 }
#             }},
#             {"range" : {
#                 "age" : {
#                     "gte" : 18,
#                     "lte" : 21
#                 }
#             }}
#         ],
#     }
# })
# print(doc_5)
