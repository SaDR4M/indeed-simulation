# from django_elasticsearch_dsl import Document , fields
# from django_elasticsearch_dsl.registries import registry
# # local imports
# from employer.models import Employer
# from account.models import User
# from payment.models import Payment
# from package.models import Package
# from order.models import Order , OrderItem


# @registry.register_document
# class EmployeOrderDocument(Document) :

#     employer = fields.NestedField(properties = {
#         "user" : fields.ObjectField(properties = {
#             "email" : fields.KeywordField(),
#             "phone" : fields.KeywordField()
#         }),
#         "address" : fields.TextField(),
#         "city" : fields.TextField(),
#         "id_number" : fields.TextField(),
#         "postal_code" : fields.TextField()
#     })
#     payment = fields.ObjectField(properties = {
#         "amount" : fields.IntegerField(),
#         "authority" : fields.KeywordField(),
#         "checkout_at" : fields.DateField(),
#         "payment_id" : fields.KeywordField(),
#         "status" : fields.KeywordField()
#     })
#     order_items = fields.NestedField(properties = {
#         "user" : fields.ObjectField(properties = {
#             "email" : fields.KeywordField(),
#             "phone" : fields.KeywordField()
#         }),
#        "package" : fields.ObjectField(properties = {
#            "price" : fields.IntegerField(),
#            "count" : fields.IntegerField(),
#            "priority" : fields.KeywordField(),
#            "type" : fields.KeywordField(),
#            "active" : fields.BooleanField(),
#            "created_at" : fields.DateField(),
#            "deleted_at" : fields.DateField(),
#        }),
#        "added_at" : fields.DateField()
#     })
    
    
#     class Index:
#         name = "emplyoer_order"
    
    
        
#     class Django :
#         model = Order
#         fields = [
#             "status" , "order_at" , "order_id"
#         ]
#     related_models = [User , Employer , Payment , OrderItem , Package]