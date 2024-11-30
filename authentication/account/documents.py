# from django_elasticsearch_dsl import Document
# from django_elasticsearch_dsl.registries import registry
# from .models import User


# @registry.register_document
# class UserDocument(Document) :
#     class Index:
#         name = "user"
        
        
#     class Django:
#         model = User
        
#         fields = [
#             "email",
#             "phone"
#         ]