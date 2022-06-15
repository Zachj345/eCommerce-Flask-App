from datetime import timedelta
from flask import Flask
from flask import render_template, request, flash, jsonify, url_for, redirect
from flask import session as sesh
from flask_login import UserMixin
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
import stripe


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret key'
app.config['STRIPE_PUBLIC_KEY'] = 'secret'
app.config['STRIPE_SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=2)
db = SQLAlchemy(app)

stripe.api_key = app.config['STRIPE_SECRET_KEY']

login_manager = LoginManager()
login_manager.login_view = 'herbs'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    cart = db.relationship('Cart', cascade='all, delete, delete-orphan',
                           backref='user', lazy=True, passive_deletes=True)
    product = db.relationship('Product', cascade='all, delete, delete-orphan',
                              backref='user', lazy=True, passive_deletes=True)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship('Product', cascade='all, delete, delete-orphan',
                            backref='cart', lazy=True, passive_deletes=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey(
        'cart.id', ondelete='CASCADE'), nullable=False)


def get_subtotal(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        flash('no user to calculate subtotal', category='error')
    else:
        return sum([i.price for i in user.product])


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    sesh.permanent = True
    try:
        user_id = current_user.id
        user = User.query.filter_by(id=user_id).first()
        cart_items = [i.title for i in user.product]
        cart_quantity = [i.count for i in user.product]
        item_dict = {i: j for i, j in zip(cart_items, cart_quantity)}
        prices_in_order = [Product.query.filter_by(
            title=i).first().price for i in list(item_dict.keys())]
        full_item_dict = {i: j for i, j in zip(
            item_dict.items(), prices_in_order)}

    except (AttributeError, UnboundLocalError):
        item_dict = {}
        full_item_dict = {}
        prices_in_order = []

    line_items = []
    if not full_item_dict:
        line_items = [{'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': 'Chamomille',
            },
            'unit_amount': 11 * 100,

        },
            'quantity': 1,


        }]
    for (title, quantity), price in full_item_dict.items():
        line_items.append({'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': title,
            },
            'unit_amount': int(price) * 100,

        },
            'quantity': quantity,


        })

    session = stripe.checkout.Session.create(
        line_items=line_items,

        mode='payment',
        success_url=url_for('checkout', _external=True) +
        '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('herbs', _external=True),
    )

    return render_template('home.html', user=current_user, item_dict=item_dict,
                           get_subtotal=get_subtotal, prices_in_order=prices_in_order, full_item_dict=full_item_dict,
                           checkout_session_id=session['id'],
                           checkout_public_key=app.config['STRIPE_PUBLIC_KEY'])


@app.route('/about', methods=['GET'])
def about():
    try:
        user_id = current_user.id
        user = User.query.filter_by(id=user_id).first()
        cart_items = [i.title for i in user.product]
        cart_quantity = [i.count for i in user.product]
        item_dict = {i: j for i, j in zip(cart_items, cart_quantity)}
        prices_in_order = [Product.query.filter_by(
            title=i).first().price for i in list(item_dict.keys())]
        full_item_dict = {i: j for i, j in zip(
            item_dict.items(), prices_in_order)}

    except (AttributeError, UnboundLocalError):
        item_dict = {}
        full_item_dict = {}
        prices_in_order = []

    line_items = []
    if not full_item_dict:
        line_items = [{'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': 'Chamomille',
            },
            'unit_amount': 11 * 100,

        },
            'quantity': 1,


        }]
    for (title, quantity), price in full_item_dict.items():
        line_items.append({'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': title,
            },
            'unit_amount': int(price) * 100,

        },
            'quantity': quantity,


        })

    session = stripe.checkout.Session.create(
        line_items=line_items,

        mode='payment',
        success_url=url_for('checkout', _external=True) +
        '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('herbs', _external=True),
    )

    return render_template('about.html', user=current_user, item_dict=item_dict,
                           prices_in_order=prices_in_order, get_subtotal=get_subtotal, full_item_dict=full_item_dict,
                           checkout_session_id=session['id'],
                           checkout_public_key=app.config['STRIPE_PUBLIC_KEY'])


@app.route('/herbs', methods=['GET', 'POST'])
def herbs():
    try:
        user_id = current_user.id
        user = User.query.filter_by(id=user_id).first()
        cart_items = [i.title for i in user.product]
        cart_quantity = [i.count for i in user.product]
        item_dict = {i: j for i, j in zip(cart_items, cart_quantity)}
        prices_in_order = [Product.query.filter_by(
            title=i).first().price for i in list(item_dict.keys())]
        full_item_dict = {i: j for i, j in zip(
            item_dict.items(), prices_in_order)}

    except (AttributeError, UnboundLocalError):
        item_dict = {}
        full_item_dict = {}
        prices_in_order = []

    line_items = []
    if not full_item_dict:
        line_items = [{'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': 'Chamomille',
            },
            'unit_amount': 11 * 100,

        },
            'quantity': 1,


        }]
    for (title, quantity), price in full_item_dict.items():
        line_items.append({'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': title,
            },
            'unit_amount': int(price) * 100,

        },
            'quantity': quantity,


        })

    session = stripe.checkout.Session.create(
        line_items=line_items,

        mode='payment',
        success_url=url_for('checkout', _external=True) +
        '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('herbs', _external=True),
    )

    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Sorry you must enter a name to browse items', category='error')
        if len(name) <= 2:
            flash('Hey, your name must be atleast 3 characters', category='error')
        else:
            user_check = User.query.filter_by(name=name).first()
            if user_check:
                flash('Please register with a different name', category='error')
                return redirect(url_for('home'))
            user = User(name=name)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)

            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()

            return redirect(url_for('herbs', user=current_user))

    print([i for i in Cart.query.all()])
    print([i for i in User.query.all()])
    return render_template('herbs.html', user=current_user, item_dict=item_dict,
                           get_subtotal=get_subtotal, full_item_dict=full_item_dict,
                           prices_in_order=prices_in_order, checkout_session_id=session['id'],
                           checkout_public_key=app.config['STRIPE_PUBLIC_KEY'])


@ app.route('/checkout', methods=["GET"])
@ login_required
def checkout():
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    try:
        cart_items = [i.title for i in user.product]
        cart_quantity = [i.count for i in user.product]
        item_dict = {i: j for i, j in zip(cart_items, cart_quantity)}
        prices_in_order = [Product.query.filter_by(
            title=i).first().price for i in list(item_dict.keys())]
        full_item_dict = {i: j for i, j in zip(
            item_dict.items(), prices_in_order)}

    except (AttributeError, UnboundLocalError):
        item_dict = {}
        full_item_dict = {}
        prices_in_order = []

    [db.session.delete(i) for i in user.product]
    db.session.commit()

    return render_template('checkout.html', user=current_user, item_dict=item_dict,
                           get_subtotal=get_subtotal, full_item_dict=full_item_dict)


@app.route('/add-product/<user_id>', methods=['POST'])
@login_required
def add_product(user_id):
    user = User.query.filter_by(id=user_id).first()
    cart_items = [i.title for i in user.product]
    cart_quantity = [i.count for i in user.product]
    item_dict = {i: j for i, j in zip(cart_items, cart_quantity)}
    prices_in_order = [Product.query.filter_by(
        title=i).first().price for i in list(item_dict.keys())]
    full_item_dict = {i: j for i, j in zip(
        item_dict.items(), prices_in_order)}
    print(full_item_dict)

    if not user:
        print('no user')
        flash(f'no user with the id of {user_id}', category='error')

    title = request.form.get('title')
    price = request.form.get('price')

    if not title:
        print('no title')

    if not price:
        print('no price')

    else:
        print('we got here finally')
        other_product = Product.query.filter_by(title=title).first()

        if other_product:
            product = Product(title=title, count=cart_items.count(title) + 1,
                              price=int(price), user_id=user_id, cart_id=user.cart[0].id)
        else:
            product = Product(title=title, count=1,
                              price=price, user_id=user_id, cart_id=user.cart[0].id)

        db.session.add(product)
        db.session.commit()
        return redirect(url_for('herbs'))
        # return jsonify({'success': 'facts', 'title': title, 'item_dict': item_dict, 'price': price})

    print(cart_items)
    print(cart_quantity)
    print(item_dict)
    print(Product.query.all())
    return jsonify({'semi-success': 'facts', 'item_dict': item_dict, 'title': title,
                    'price': price})

    # return render_template('herbs.html', user=current_user, item_dict=item_dict,
    #                        get_subtotal=get_subtotal, full_item_dict=full_item_dict)


@ app.route('/return-policy', methods=['GET'])
def returns():
    try:
        user_id = current_user.id
        user = User.query.filter_by(id=user_id).first()
        cart_items = [i.title for i in user.product]
        cart_quantity = [i.count for i in user.product]
        item_dict = {i: j for i, j in zip(cart_items, cart_quantity)}
        prices_in_order = [Product.query.filter_by(
            title=i).first().price for i in list(item_dict.keys())]
        full_item_dict = {i: j for i, j in zip(
            item_dict.items(), prices_in_order)}

    except (AttributeError, UnboundLocalError):
        item_dict = {}
        full_item_dict = {}
        prices_in_order = []

    return render_template('return-policy.html', user=current_user, item_dict=item_dict,
                           get_subtotal=get_subtotal, full_item_dict=full_item_dict)


@ app.route('/del-user/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        print('no user')
    if user.cart:
        [db.session.delete(i) for i in user.cart]
    if user.product:
        [db.session.delete(i) for i in user.product]
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('home'))


@ app.route('/del-cart/<int:id>', methods=['GET', 'POST'])
def delete_cart(id):
    cart = Cart.query.filter_by(id=id).first()
    if not cart:
        print('no user')
    db.session.delete(cart)
    db.session.commit()
    return redirect(url_for('home'))


@ app.route('/del-product/<title>', methods=["GET", "POST"])
@ login_required
def del_product(title):
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'This user doesn\'t exist'}, 400)
    else:
        products = list(filter(lambda n: n.title == title, user.product))
        print(products)
        if not products:
            return jsonify({'error': 'Product doesn\'t exist in your cart'}, 400)
        else:
            [db.session.delete(i) for i in products]
            db.session.commit()
            print([i for i in products])

    return jsonify({'success': 'facts'})


# maybe pop the first product that matches that name/id out of user.products and make the min 0
@ app.route('/sub-quantity/<title>', methods=["GET", "POST"])
@ login_required
def sub_quantity(title):
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'error': 'This user doesn\'t exist'}, 400)
    else:
        products = list(filter(lambda n: n.title == title, user.product))
        print(products)
        if not products:
            return jsonify({'error': 'Product is not in your cart'}, 400)
        else:
            try:
                db.session.delete(products.pop())
                db.session.commit()
            except IndexError:
                pass
            print([i for i in products])
    return jsonify({'success': 'facts'})


@ app.route('/add-quantity/<title>', methods=["GET", "POST"])
@ login_required
def add_quantity(title):
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    cart_items = [i.title for i in user.product]

    if not user:
        return jsonify({'error': 'This user doesn\'t exist'}, 400)
    else:
        other_product = Product.query.filter_by(title=title).first()

        product = Product(title=title, count=cart_items.count(title) + 1,
                          price=other_product.price, user_id=user_id, cart_id=user.cart[0].id)

        db.session.add(product)
        db.session.commit()
    return jsonify({'success': 'facts'})


if __name__ == '__main__':
    app.run(debug=True, port=8050)
