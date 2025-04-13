from rest_framework import serializers
# local imports
from employer.models import Employer
from manager.models import TechnologyCategory


class GetEmployerSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Employer
        fields = '__all__'
        
class TechnologyCategoryCreateSerializer(serializers.ModelSerializer) :
    class Meta :
        model = TechnologyCategory
        exclude = ['created_by']
        
class TechnologyCategoryUpdateSerializer(serializers.ModelSerializer) :
    class Meta :
        model = TechnologyCategory
        fields = ['name' , 'description']  
         
class TechnologyCategoryShowSerializer(serializers.ModelSerializer) :
    class Meta :
        model = TechnologyCategory
        fields = ['id' , 'name' , 'description']