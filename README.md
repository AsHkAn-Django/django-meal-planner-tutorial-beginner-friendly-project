# Django Meal Planner 🍽️🛒

A full-featured Django web app that lets users plan meals for the week and automatically generates a smart, aggregated grocery list.

## Features

- Auto-generated grocery list based on selected meals
- Aggregates ingredient quantities (e.g., 2× + 3× carrots → 5×)
- Persistent weekly planning per user
- Easily editable and up-to-date meal schedules

## Tech Stack

- Python & Django
- HTML5, CSS3
- Bootstrap

## Turtorial

#### recipe and ingredients models

```python
class Ingredient(models.Model):
    title = models.CharField(max_length=264, unique=True)
    picture = models.ImageField(upload_to='images/')

class Recipe(models.Model):
    title = models.CharField(max_length=264)
    instruction = models.CharField(max_length=264)
    picture = models.ImageField(upload_to='images/')
    # Created a ManyToManyField to the Ingredient model through the RecipeIngredient model.
    # Why use 'through'? Because we need access to additional information about the relationship,
    # such as the amount of each ingredient and its order in the recipe.
    # Use the 'through' option whenever you need to store or access extra data in a many-to-many relationship.
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')

def get_average_rating(self):
    '''Bring the average rating for this recipe.'''
    ratings = self.ratings.all()
    if not ratings:
        return Decimal('0.0')
    else:
        total = sum(rating.rate for rating in ratings)
    return Decimal(round(total / len(ratings), 1))

class RecipeIngredient(models.Model):
    '''The bridge between recipe and ingredient for checking the amount and order.'''
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    # amount will be handled better in the next versions. or you can try changing it :)
    amount = models.CharField(max_length=100)
    order = models.PositiveIntegerField()

class Meta:
    unique_together = (('recipe', 'ingredient', 'order'),)
    ordering = ['order']
```

#### MealPlan model for storing a meal for a specific day of the week

```python
class MealPlan(models.Model):

    class DayOfWeek(models.TextChoices):
        '''A textchoices class for keeping the days of a week'''
        MONDAY = 'MON', 'Monday'
        TUESDAY = 'TUE', 'Tuesday'
        WEDNESDAY = 'WED', 'Wednesday'
        THURSDAY = 'THU', 'Thursday'
        FRIDAY = 'FRI', 'Friday'
        SATURDAY = 'SAT', 'Saturday'
        SUNDAY = 'SUN', 'Sunday'

    class MealSlot(models.TextChoices):
        '''A textchoices class for keeping the meals of a day.'''
        BREAKFAST = 'BF', 'Breakfast'
        LUNCH     = 'LU', 'Lunch'
        DINNER    = 'DI', 'Dinner'

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="meal_plans_recipe")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans_user")
    day = models.CharField(max_length=3, choices=DayOfWeek.choices)
    slot = models.CharField(max_length=2, choices=MealSlot.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Prevent duplicate ingredient entry

```python
class AddIngredientView(generic.CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "myApp/add_ingredient.html"
    success_url = reverse_lazy('myApp:add_ingredient')

    def form_valid(self, form):
        category_name = form.cleaned_data.get('title')
        # If the ingredient exists show an error and dont save it.
        if Ingredient.objects.filter(title__iexact=category_name).exists():
            form.add_error('title', 'This ingridient already exists.')
            messages.warning(self.request, 'Duplicate ingredient!')
            return self.form_invalid(form)
        # If the form was valid show the user a success message.
        messages.success(self.request, 'The ingredient has been added successfully.')
        return super().form_valid(form)
```

#### Rate and review a recipe

```python
class RatingFormView(LoginRequiredMixin, generic.FormView):
    model = Rating
    form_class = RatingForm
    success_url = reverse_lazy('myApp:home')
    template_name = "myApp/rating_form.html"

    def form_valid(self, form):
        '''If a rate exists delete it and save the new one.'''
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
```

#### Handling the order of the ingredients and amounts in `RecipeIngredient` model

```python
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
        # set the order the lenght of the objects of this model for this recipe(so it starts from 0 and goes up)
        form.instance.order = len(RecipeIngredient.objects.filter(recipe__title__iexact=recipe_name))

        # If the form was valid show the user a success message.
        messages.success(self.request, 'The ingredient and amount have been added successfully.')
        return super().form_valid(form)
```

#### Getting the list of ingredients and amounts for shopping list

```python
class WeeklyRecipePlan(generic.ListView):
    model = MealPlan
    template_name = 'myApp/weekly_recipe_plan.html'
    ordering = ['day']
    context_object_name = 'meals'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meals = Recipe.objects.filter(meal_plans_recipe__user=self.request.user)
        # value_list gives you a list of tupples [(50 gr, sugar), ...]
        context['shopping_list']= meals.values_list('recipe_ingredients__amount', 'recipe_ingredients__ingredient__title')
        return context
```

- then in the html you can show them like this:

```html
{% for amount, ingredient in shopping_list %}

  {{ ingredient }}
  {{ amount }}

{% empty %}
  
  No items needed.

{% endfor %}
```
- and the plan table
```html
{% for code,label in meals.0.DayOfWeek.choices %}
<tr>
    <th scope="row">{{ label }}</th>
    {% for slot_code,slot_label in meals.0.MealSlot.choices %}
    <td>
    {% for meal in meals %} 
        {% if meal.day == code and meal.slot == slot_code %}
        <a href="{% url 'myApp:recipe_detail' meal.recipe.id %}">{{ meal.recipe.title }}</a>
        {% endif %} 
        {% empty %}
        <span class="text-muted">—</span>
    {% endfor %}
    </td>
    {% endfor %}
</tr>
{% endfor %}
```
