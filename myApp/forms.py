from django import forms
from .models import Ingredient, Recipe, Rating, RecipeIngredient, MealPlan


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ['ingredients',]
        

class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        exclude = ['order',]
        

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rate', 'review']
        labels = {
            'rate': 'Rate between 1-5',
            'review': 'Review'
        }
        widgets = {
            'rate': forms.NumberInput(attrs={'placeholder': 'Ex: 3.5'}),
            'review': forms.Textarea(attrs={'placeholder': 'Write your review here...'}),
        }
        
        
class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['recipe', 'day', 'slot']
        