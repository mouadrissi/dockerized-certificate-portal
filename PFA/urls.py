from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('certificates.urls')), 
]

urlpatterns += static('/attestations/', document_root=settings.BASE_DIR / 'attestations')