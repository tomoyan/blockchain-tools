from flask import Flask, render_template, redirect, request, flash, jsonify
from config import Config
from forms import UserNameForm
# from forms import postUrlForm
# from markupsafe import escape
# import BlurtChain as BC


app = Flask(__name__)
app.config.from_object(Config)


@app.errorhandler(404)
# This handles 404 error
def page_not_found(e):
    return render_template('404.html')


@app.route('/', methods=['GET', 'POST'])
def blurt():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect(f'/{username}')
        else:
            flash('Username is Required')

    return render_template('blurt/profile.html', form=form)


if __name__ == "__main__":
    app.run()
