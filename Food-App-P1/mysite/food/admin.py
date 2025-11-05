from django.contrib import admin
from food.models import FoodItemsModel, LogHistoryMode

# Register your models here.
# -------------------------------------------------------------------------------------------- 
admin.site.register(FoodItemsModel)
admin.site.register(LogHistoryMode)
