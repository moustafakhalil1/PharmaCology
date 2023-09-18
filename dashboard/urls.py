from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns=[
  path('register/',views.registerPage,name='register_login'),
  path('login/',views.LoginPage,name="login"),
  path('ocr/',views.ocrPage,name="ocr"),
  path('Logout/',views.logoutPage,name="logout"),
  path('crop/',views.image_crop_view,name='crop'),
  path('ocr/ss',views.voice,name='voice'),
  path('',views.handwriting_dashboard,name='home'),
 


]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)