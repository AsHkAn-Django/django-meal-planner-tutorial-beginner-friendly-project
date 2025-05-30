from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .models import Ingredient, Recipe, Rating, RecipeIngredient, MealPlan
from .forms import IngredientForm, RecipeForm, RatingForm, RecipeIngredientForm, MealPlanForm



class IndexView(generic.ListView):
    model = Recipe
    context_object_name = 'recipes'
    template_name = "myApp/index.html"
        

class RecipeDetailView(generic.DetailView):
    model = Recipe
    template_name = "myApp/recipe_detail.html"
    context_object_name = 'recipe'


class AddIngredientView(generic.CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "myApp/add_ingredient.html"
    success_url = reverse_lazy('myApp:add_ingredient')
    
    def form_valid(self, form):
        category_name = form.cleaned_data.get('title')
        if Ingredient.objects.filter(title__iexact=category_name).exists():
            form.add_error('title', 'This ingridient already exists.')
            messages.warning(self.request, 'Duplicate ingredient!')
            return self.form_invalid(form)
        # If the form was valid show the user a success message.
        messages.success(self.request, 'The ingredient has been added successfully.')
        return super().form_valid(form)
    

class AddRecipeView(generic.CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "myApp/add_recipe.html"
    success_url = reverse_lazy('myApp:add_recipe_ingredient')

    def form_valid(self, form):
        # If the form was valid show the user a success message.        
        messages.success(self.request, 'The recipe has been added successfully.')
        return super().form_valid(form)
    
    
class FilterListView(generic.ListView):
    template_name = "myApp/filter_list.html"
    context_object_name = 'recipes'

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            return Recipe.objects.filter(Q(title__icontains=query) | 
                                         Q(instruction__icontains=query) | 
                                         Q(ingredients__title__icontains=query)).distinct()
        return Recipe.objects.none()


class RatingFormView(LoginRequiredMixin, generic.FormView):
    model = Rating
    form_class = RatingForm
    success_url = reverse_lazy('myApp:home')
    template_name = "myApp/rating_form.html"
    
    def form_valid(self, form):
        recipe_id = self.kwargs.get('pk')
        rate_exist = Rating.objects.filter(recipe_id=recipe_id, user=self.request.user)
        if rate_exist:
            rate_exist.delete()
        form.instance.user = self.request.user
        form.instance.recipe = get_object_or_404(Recipe, id=recipe_id)
        form.save()
        messages.success(self.request, 'You have rated the recipe successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe_id = self.kwargs.get('pk')
        context['recipe'] = get_object_or_404(Recipe, id=recipe_id)
        return context
    
    
    
class AddRecipeIngredientView(generic.CreateView):
    model = RecipeIngredient
    form_class = RecipeIngredientForm
    template_name = "myApp/add_recipe_ingredient.html"
    success_url = reverse_lazy('myApp:add_recipe_ingredient')
    
    def form_valid(self, form):
        ingredient_name = form.cleaned_data.get('ingredient')
        if RecipeIngredient.objects.filter(ingredient__title__iexact=ingredient_name).exists():
            form.add_error('ingredient', 'This ingridient already exists.')
            messages.warning(self.request, 'Duplicate ingredient!')
            return self.form_invalid(form)
        recipe_name = form.cleaned_data.get('recipe')
        form.instance.order = len(RecipeIngredient.objects.filter(recipe__title__iexact=recipe_name))
        
        # If the form was valid show the user a success message.
        messages.success(self.request, 'The ingredient and amount have been added successfully.')
        return super().form_valid(form)
    
    

class AddMealPlanView(generic.CreateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = "myApp/add_meal_plan.html"
    success_url = reverse_lazy('myApp:add_meal_plan')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'The recipe has been added to the plan successfully.')
        return super().form_valid(form)
    
    
class WeeklyRecipePlan(generic.ListView):
    model = MealPlan
    template_name = 'myApp/weekly_recipe_plan.html'
    ordering = ['day']
    context_object_name = 'meals'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meals = Recipe.objects.filter(meal_plans_recipe__user=self.request.user)
        context['shopping_list']= meals.values_list('recipe_ingredients__amount', 'recipe_ingredients__ingredient__title')
        return context               
    
    