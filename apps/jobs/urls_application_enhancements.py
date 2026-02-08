"""
URL configuration for application enhancement endpoints.
"""
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views_application_enhancements

app_name = 'applications_enhancements'

# Router for ViewSets
router = SimpleRouter()
router.register(r'notes', views_application_enhancements.ApplicationNoteViewSet, basename='application-note')
router.register(r'status-history', views_application_enhancements.ApplicationStatusHistoryViewSet, basename='application-status-history')
router.register(r'screening-questions', views_application_enhancements.ScreeningQuestionViewSet, basename='screening-question')
router.register(r'screening-answers', views_application_enhancements.ScreeningAnswerViewSet, basename='screening-answer')
router.register(r'stages', views_application_enhancements.ApplicationStageViewSet, basename='application-stage')
router.register(r'interviews', views_application_enhancements.InterviewViewSet, basename='interview')
router.register(r'scores', views_application_enhancements.ApplicationScoreViewSet, basename='application-score')
router.register(r'templates', views_application_enhancements.ApplicationTemplateViewSet, basename='application-template')

urlpatterns = [
    # Application enhancement endpoints
    path('<uuid:application_id>/withdraw/', views_application_enhancements.withdraw_application, name='withdraw-application'),
] + router.urls
