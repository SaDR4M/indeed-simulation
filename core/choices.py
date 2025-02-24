from django.db import models

class ExperienceChoices(models.TextChoices) :
    INTERN = "intern"
    JUNIOR = "junior"
    MIDLEVEL = "midlevel"
    SENIOR = "senior"
    LEAD = "lead"
        
class CooperationChoices(models.TextChoices) :
    FULLTIME = "full_time"
    PARTTIME = "part_time"
    PROJECT = "project"
        
class WorkModeChoices(models.TextChoices) :
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    
    
class EducationChoices(models.TextChoices) :
        UNDER_DIPLOMA = "under_diploma" 
        BACHELOR = "bachelor"
        DIPLOMA = "diploma"
        MASTER =  "master"
        PHD = "phd"