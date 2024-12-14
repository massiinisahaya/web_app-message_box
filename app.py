from flask import Flask, flash, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from config import User
from peewee import IntegrityError

# 初期設定のまとめ
app = Flask(__name__)
app.secret_key = "secret"  # 秘密鍵を設定
login_manager = LoginManager()
login_manager.init_app(app)  # flaskの初期化したときの3行前のapp


# Flask-Loginがユーザー情報を取得するためのメソッド
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# ログインしていなければアクセスできないページにいった時、/loginに飛ぶ
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 入力データの検証、未入力の確認
        if not request.form["name"] or not request.form["password"] or not request.form["email"]:
            flash("未入力の項目があります")
            return redirect(request.url)

        # 入力データの検証、名前の重複確認
        if User.select().where(User.name == request.form["name"]):
            flash("その名前がすでに使われています。")
            return redirect(request.url)
        # 入力データの検証、メールの重複確認
        if User.select().where(User.email == request.form["email"]):
            flash("そのメールアドレスはすでに使われています。")
            return redirect(request.url)

        # ユーザー登録処理
        try:
            User.create(
                name=request.form["name"],
                email=request.form["email"],
                password=generate_password_hash(request.form["password"]),
            )
            return render_template("index.html")
        except IntegrityError as e:
            flash(f"{e}")

    return render_template("register.html")


# ログインフォームの表示・ログイン処理
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # データの検証
        if not request.form["password"] or not request.form["email"]:
            flash("未入力の項目があります")
            return redirect(request.url)

        # ここでユーザー認証、OKならログイン
        user = User.select().where(User.email == request.form["email"]).first()
        if user is not None and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            flash(f"ようこそ！{user.name}さん")
            return redirect(url_for("index"))

        # NGならフラッシュメッセージを設定
        flash("認証失敗しました。")

    return render_template("login.html")


# ログアウト処理
@app.route("/logout")
@login_required
def logout():
    if not current_user.is_authenticated:
        return "ログインしていません"
    logout_user()
    flash("ログアウトしました")
    return redirect(url_for("index"))


# ユーザー削除処理
@app.route("/unregister")
@login_required
def unregister():
    current_user.delete_instance()
    logout_user()
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
