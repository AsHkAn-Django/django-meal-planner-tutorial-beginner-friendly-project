from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from decimal import Decimal


class Ingredient(models.Model):
    title = models.CharField(max_length=264, unique=True)
    picture = models.ImageField(upload_to='images/')
    
    def __str__(self):
        return self.title


class Recipe(models.Model):
    title = models.CharField(max_length=264)
    instruction = models.CharField(max_length=264)
    picture = models.ImageField(upload_to='images/')    
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')

    def get_average_rating(self):
        ratings = self.ratings.all()
        if not ratings:
            return Decimal('0.0')
        else:
            total = sum(rating.rate for rating in ratings)            
        return Decimal(round(total / len(ratings), 1))
    
    # TODO: Or a better wayyyyy: 
    # from django.db.models import Avg
    # from decimal import Decimal
    # def get_average_rating(self):
    #     avg_rating = self.ratings.aggregate(avg=Avg("rate"))["avg"]
    #     return Decimal(round(avg_rating, 1)) if avg_rating is not None else Decimal("0.0")
    
    def __str__(self):
        return self.title    
    

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.CharField(max_length=100)  
    order = models.PositiveIntegerField()  

    class Meta:
        unique_together = (('recipe', 'ingredient', 'order'),)
        ordering = ['order'] 

    def __str__(self):
        return f"{self.amount} {self.ingredient.title} in {self.recipe.title}"


class Rating(models.Model):
    rate = models.DecimalField(max_digits=2, decimal_places=1, validators=[MaxValueValidator(5.0), MinValueValidator(1.0)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    date = models.DateTimeField(auto_now=True)
    review = models.CharField(max_length=250, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} rated {self.rate} to {self.recipe.title}" 


class MealPlan(models.Model):
    
    class DayOfWeek(models.TextChoices):
        MONDAY = 'MON', 'Monday'
        TUESDAY = 'TUE', 'Tuesday'
        WEDNESDAY = 'WED', 'Wednesday'
        THURSDAY = 'THU', 'Thursday'
        FRIDAY = 'FRI', 'Friday'
        SATURDAY = 'SAT', 'Saturday'
        SUNDAY = 'SUN', 'Sunday'
        
    class MealSlot(models.TextChoices):
        BREAKFAST = 'BF', 'Breakfast'
        LUNCH     = 'LU', 'Lunch'
        DINNER    = 'DI', 'Dinner'
        
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="meal_plans_recipe")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans_user")
    day = models.CharField(max_length=3, choices=DayOfWeek.choices)
    slot = models.CharField(max_length=2, choices=MealSlot.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    
    def __str__(self):
        return f"{self.user.username} added {self.recipe.title} to {self.day}"