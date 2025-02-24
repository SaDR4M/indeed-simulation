# third party imports
from rest_framework import serializers
# local imports
from job_seeker.models import Test , Question , Answer




class TestSerializer(serializers.ModelSerializer) :
    
    class Meta :
        model = Test
        exclude = ['user']
        
    def update(self , instance , validated_data) :
        
        restriced_fields = ['created_at' , 'deleted_at']
        for field in restriced_fields :
            if field in validated_data :
                raise serializers.ValidationError({field : "this field can not be updated"})
        return super().update(instance , validated_data)


class QuestionSerializer(serializers.ModelSerializer) :
    
    class Meta :
        model = Question
        exclude = ['test' , 'user']
    
    
    def update(self , instance , validated_data) :
        
        restriced_fields = ['created_at' , 'deleted_at']
        for field in restriced_fields :
            if field in validated_data :
                raise serializers.ValidationError({field : "this field can not be updated"})
        return super().update(instance , validated_data)
    
    
class AnswerSerializer(serializers.ModelSerializer) :
    
    class Meta :
        model = Answer
        exclude = ['question' , 'user']
    
    
    def update(self , instance , validated_data) :
        
        restriced_fields = ['created_at' , 'deleted_at']
        for field in restriced_fields :
            if field in validated_data :
                raise serializers.ValidationError({field : "this field can not be updated"})
        return super().update(instance , validated_data)