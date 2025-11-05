from django import forms 
from food.models import FoodItemsModel 

class FoodItemsForm(forms.ModelForm):
    class Meta:
        model = FoodItemsModel
        fields = ['prod_code', 'item_name', 'item_description', 'item_price', 'item_image']
