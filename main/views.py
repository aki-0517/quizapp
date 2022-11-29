from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import auth
from django.contrib.auth import views as auth_views  # 追加
from .forms import LoginForm, SignUpForm,QuizForm, QuestionForm, ChoiceForm
from django.contrib.auth.decorators import login_required 
from .models import Quiz, Choice, QuizAnswer # 追加
from django.db.models import Avg # 追加


def index(request):
    return render(request, "main/index.html")


def signup(request):
    if request.method == "GET":
        form = SignUpForm()
    elif request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)

            return redirect("index")

    context = {"form": form}
    return render(request, "main/signup.html", context)


class LoginView(auth_views.LoginView):
    authentication_form = LoginForm  # ログイン用のフォームを指定
    template_name = "main/login.html"  # テンプレートを指定

def home(request):
    return render(request, "main/home.html")    

@login_required # ログインしている場合にビュー関数を実行する
def create_quiz(request):
    if request.method == "GET":
        quiz_form = QuizForm()
    elif request.method == "POST":
        # 送信内容の取得
        quiz_form = QuizForm(request.POST)
        # 送信内容の検証
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            # クイズ作成者を与えて保存
            user = request.user
            quiz.user = user
            quiz.save()
            # 質問作成画面に遷移する
            return redirect("create_question", quiz.id)
    context = {
        "quiz_form":quiz_form,
    }
    return render(request, "main/create_quiz.html", context)
def create_question(request, quiz_id):
    # Quiz オブジェクトから id が前画面で作成したオブジェクトの id に等しいものを取得する
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # 現在データベースに保存されている質問の数
    current_question_num = quiz.question_set.all().count()
    # 次に質問を作成した際にデータベースに保存される質問の数
    next_question_num = current_question_num + 1
    if request.method == "GET":
        question_form = QuestionForm()
        choice_form = ChoiceForm()
    elif request.method == "POST":
        # 送信内容の取得
        question_form = QuestionForm(request.POST)
        # 送信された 4 つの選択肢のテキストを取得
        choices = request.POST.getlist("choice")
        # 正解選択肢の id を取得
        answer_choice_num = request.POST["is_answer"]
        # 送信内容の検証
        if question_form.is_valid():
            question = question_form.save(commit=False)
            # 送信内容を保存する
            question.quiz = quiz
            question.save()
            # Choice モデルにデータを保存する
            for i, choice in enumerate(choices):
                # 正解選択肢には is_answer を True にして保存する
                if i == int(answer_choice_num):
                    Choice.objects.create(
                        question=question, choice=choice, is_answer=True
                    )
                else:
                    Choice.objects.create(
                        question=question, choice=choice, is_answer=False
                    )
            return redirect("create_question", quiz_id)
    context = {
        "question_form":question_form,
        "choice_form":choice_form,
        "quiz_id" : quiz_id,
        "next_question_num" : next_question_num,
    }
    return render(request, "main/create_question.html", context)

def answer_quiz_list(request):
    user = request.user
    # 自分以外のユーザーが作成したクイズオブジェクトを取得する
    quiz_list = Quiz.objects.exclude(user=user)
    context = {
        "quiz_list":quiz_list,
    }
    return render(request, "main/answer_quiz_list.html", context)



def answer_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # quiz に紐づく全ての question を取得する
    questions = quiz.question_set.all()
    score = 0

    # 追加
    # question オブジェクトの数を集計する
    question_num = questions.count()
    user = request.user
    print(type(user))

    if request.method == "POST":
        for question in questions:
            # 質問ごとにラジオボタンをグループ分けした質問ごとの選択肢の id を取得する
            choice_id = request.POST.get(str(question.id))
            choice_obj = get_object_or_404(Choice, id=choice_id)
            # 選択した選択肢が正解なら得点を増やす
            if choice_obj.is_answer:
                score += 1

        # 追加
        # 得点率を計算する
        answer_rate = score*100/question_num
        # 得点と得点率をデータベースに保存する
        QuizAnswer.objects.create(
            user=user,
            quiz=quiz,
            score=score,
            answer_rate=answer_rate,
        )

        answer_rate = score*100/question_num
        QuizAnswer.objects.create(user=user, quiz=quiz, score=score, answer_rate=answer_rate)

        return redirect("result", quiz_id)
   
    context = {
        "quiz":quiz,
        "questions":questions,
    }
    return render(request, "main/answer_quiz.html", context)

def result(request, quiz_id):
    user = request.user
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz_answer = QuizAnswer.objects.filter(quiz=quiz, user=user).order_by("answered_at").last()
    context = {
        "quiz_answer":quiz_answer,
    }

    return render(request, "main/result.html", context)    