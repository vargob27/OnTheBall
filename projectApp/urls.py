from django.urls import path     
from . import views

urlpatterns = [
    path('', views.success),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('home', views.success),
    path('user/<int:user_id>', views.profile),
    path('user/<int:user_id>/edit', views.edit_profile),
    path('user/<int:user_id>/update', views.update_profile),
    path('event/create', views.createEvent),
    path('event/<int:event_id>', views.event),
    path('event/<int:event_id>/edit', views.editEvent),
    path('event/<int:event_id>/update', views.updateEvent),
    path('event/<int:event_id>/delete', views.deleteEvent),
    path('event/<int:event_id>/attend', views.attendEvent),
    path('event/<int:event_id>/unattended', views.unattendedEvent),
    path('like/<int:event_id>/<int:id>', views.add_like),
    path('unlike/<int:event_id>/<int:id>', views.remove_like),
    path('comment/<int:event_id>', views.comment),
    path('<int:event_id>/comment/<int:post_id>/edit', views.editComment),
    path('<int:event_id>/comment/<int:post_id>/update', views.updateComment),
    path('<int:event_id>/comment/<int:post_id>/delete', views.deleteComment),
    path('find/<str:sport>', views.find),
    # available
    path('sorted', views.allEvents),
    path('test', views.test)
]