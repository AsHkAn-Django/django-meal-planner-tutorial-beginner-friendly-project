from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


app_name = 'myApp'
urlpatterns = [
    path('recipe_detail/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('rating_form/<int:pk>/', views.RatingFormView.as_view(), name='rating_form'),    
    path('filter_list/', views.FilterListView.as_view(), name='filter_list'),
    path('add_ingredient/', views.AddIngredientView.as_view(), name='add_ingredient'),
    path('add_recipe/', views.AddRecipeView.as_view(), name='add_recipe'),    
    path('', views.IndexView.as_view(), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)