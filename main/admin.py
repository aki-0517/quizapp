from django.contrib import admin

from .models import User, Quiz, Question, Choice, QuizAnswer

admin.site.register(User)
admin.site.register(Quiz) # 追加
admin.site.register(Question) # 追加
admin.site.register(Choice) # 追加
admin.site.register(QuizAnswer)