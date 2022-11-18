from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('products/', views.ProductList.as_view()),
    path('products/<int:product_id>/', views.ProductDetail.as_view()),
    path('products/<int:product_id>/reviews/', views.ReviewList.as_view()),
    path('products/<int:product_id>/reviews/<int:review_id>/', views.ReviewDetail.as_view()),
    path('cart/', views.CreateCart.as_view()),

]
