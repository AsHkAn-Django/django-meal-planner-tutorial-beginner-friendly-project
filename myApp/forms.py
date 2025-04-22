from django import forms
from .models import Ingredient, Recipe, Rating, RecipeIngredient


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
        
        
        
        
# TODO:  First user fills the recipe form
# then we send him to the next page which is the igredients with amounts(RecipeIngredient)
# In here user can search the ingredient and write the amount for it and add
# if the ingredient is not there user can go to another page and add it
# for everytime the user submits the ingredient form the oder will be equal to the length of RecipeIngredient objects 
# so it starts from 0 to ++