
import os, sqlite3, uuid, secrets
from functools import wraps
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = BASE / "store.db"
ALLOWED = {"png", "jpg", "jpeg", "webp", "gif"}
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "27698881104")
ADMIN_NAME = os.environ.get("ADMIN_NAME", "Otsile")
ADMIN_PHONE = os.environ.get("ADMIN_PHONE", "0698881104")

PRICE_LIST = {
    "Mind Full of Money Design": [("Hoodies",350),("Sweatshirts",300),("T-Shirts",300),("Sweatpants",200),("Panel Caps",130)],
    "Young Money Design": [("Hoodies",350),("Sweatshirts",300),("T-Shirts",200),("Sweatpants",200)],
    "Classic Design": [("Hoodies",350),("Sweatshirts",300),("T-Shirts",300),("Sweatpants",200),("Panel Caps",130)],
    "Boys Club and Girls Club Design": [("Hoodies",380),("Sweatshirts",350),("T-Shirts",250),("Sweatpants",220),("Girls Crop Tops",200)],
    "Newspaper Design": [("Hoodies",380),("Sweatshirts",350),("T-Shirts",250),("Sweatpants",220)],
    "Only Cure for the Struggle Design": [("Hoodies",380),("Sweatshirts",350),("T-Shirts",250),("Sweatpants",220)],
    "HN Design": [("Hooded",400),("Sweatshirts",350),("T-Shirts",250),("Sweatpants",220)],
    "Classic Edition Design": [("Hoodies",400),("Sweatshirts",350),("T-Shirts",250),("Sweatpants",220),("Panel Caps",150)],
    "Hustle Nation Accessories": [("Beanies",100),("Gloves",100),("School Bag",300)],
    "Mafia Tracksuits": [("Full Zip Mafia Top",500),("Mafia Pants",400),("Mafia Shorts",200),("2-Piece Mafia",900)],
    "2nd Edition Mafia (Not Yet Released)": [("Mafia Top",550),("Mafia Trackpants",450),("Mafia Shorts",300),("2-Piece Mafia",1000),("Mafia Top and Shorts Set",600)]
}

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS products(
          id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, name TEXT NOT NULL,
          price INTEGER NOT NULL, description TEXT DEFAULT '', image TEXT DEFAULT '',
          sizes TEXT DEFAULT 'S, M, L, XL, XXL', colors TEXT DEFAULT 'Black, White',
          stock INTEGER DEFAULT 0, active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS customers(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
          id_number TEXT NOT NULL, street TEXT NOT NULL, password_hash TEXT NOT NULL,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS orders(
          id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, customer_name TEXT,
          email TEXT, items_json TEXT NOT NULL, total INTEGER NOT NULL, status TEXT DEFAULT 'WhatsApp enquiry',
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS gallery(
          id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, image TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        count = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            for category, items in PRICE_LIST.items():
                for name, price in items:
                    c.execute("INSERT INTO products(category,name,price,description,stock) VALUES(?,?,?,?,?)",
                              (category,name,price,"Add product details in the creator dashboard.",0))
        defaults = {
            "store_name":"HUSTLE NATION", "launch_date":"4 December 2026",
            "launch_notice":"OUR STORE IS LAUNCHING 4 DECEMBER 2026 — BE PART OF THE JOURNEY.",
            "about":"Hustle Nation is a streetwear clothing brand built around creativity, confidence and the hustle. Explore our collections and contact us on WhatsApp to place an order.",
            "terms":"Orders are confirmed directly with our team on WhatsApp. Prices are shown in South African Rand (R) and may be updated by the store. Product availability, sizes, colours, delivery or collection arrangements and final order totals must be confirmed before payment. Do not send payment to an unverified number. Customised items may have separate production times. Please contact us promptly if there is an issue with an order.",
            "theme":"red", "logo":"hustle-nation-logo.jpg", "loader_logo":"hustle-nation-logo.jpg", "loader_theme":"black", "maintenance":"0",
            "maintenance_message":"We are making improvements. Please check back soon.",
            "whatsapp":WHATSAPP_NUMBER, "instagram":"hustle_nation_apparel1_", "tiktok":"HUSTLE NATION APPAREL",
            "facebook":"Hustle Nation Apparel", "currency":"R"
        }
        for k,v in defaults.items():
            c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",(k,v))

def settings():
    with db() as c:
        return {r["key"]:r["value"] for r in c.execute("SELECT key,value FROM settings")}

def set_setting(key, value):
    with db() as c:
        c.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(key,value))

def customer_required(f):
    @wraps(f)
    def wrap(*a,**kw):
        if not session.get("customer_id"):
            flash("Please log in or create an account to continue.", "warning")
            return redirect(url_for("login"))
        return f(*a,**kw)
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*a,**kw):
        if not session.get("admin"):
            return redirect(url_for("creator_login"))
        return f(*a,**kw)
    return wrap

def save_image(file):
    if not file or not file.filename:
        return ""
    ext = file.filename.rsplit(".",1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED:
        raise ValueError("Use PNG, JPG, JPEG, WEBP or GIF images.")
    name = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    file.save(UPLOAD_DIR / name)
    return name

@app.context_processor
def inject_globals():
    return {"site":settings(), "cart_count":len(session.get("cart",[])), "logged_customer":session.get("customer_name")}

@app.before_request
def maintenance_guard():
    if request.endpoint in {"creator_login","creator_logout","static","maintenance"}:
        return
    s = settings()
    if s.get("maintenance") == "1" and not session.get("admin"):
        return render_template("maintenance.html", site=s), 503

@app.route("/")
def home():
    s=settings()
    with db() as c:
        products=c.execute("SELECT * FROM products WHERE active=1 ORDER BY category,name").fetchall()
        categories=c.execute("SELECT DISTINCT category FROM products WHERE active=1 ORDER BY category").fetchall()
    return render_template("home.html", products=products, categories=[x["category"] for x in categories], site=s)

@app.route("/product/<int:pid>")
def product(pid):
    with db() as c: p=c.execute("SELECT * FROM products WHERE id=? AND active=1",(pid,)).fetchone()
    if not p: abort(404)
    return render_template("product.html", p=p)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip().lower()
        idn=request.form.get("id_number","").strip(); street=request.form.get("street","").strip()
        password=request.form.get("password","")
        if not all([name,email,idn,street,password]) or len(password)<8:
            flash("Complete every field. Password must have at least 8 characters.","error")
        else:
            try:
                with db() as c:
                    c.execute("INSERT INTO customers(name,email,id_number,street,password_hash) VALUES(?,?,?,?,?)",
                              (name,email,idn,street,generate_password_hash(password)))
                flash("Account created. You can now log in.","success"); return redirect(url_for("login"))
            except sqlite3.IntegrityError: flash("That email address already has an account.","error")
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email","").strip().lower(); password=request.form.get("password","")
        with db() as c: user=c.execute("SELECT * FROM customers WHERE email=?",(email,)).fetchone()
        if user and check_password_hash(user["password_hash"],password):
            session["customer_id"]=user["id"]; session["customer_name"]=user["name"]
            flash("Welcome back.","success"); return redirect(url_for("home"))
        flash("Email or password is incorrect.","error")
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.pop("customer_id",None); session.pop("customer_name",None)
    return redirect(url_for("home"))

@app.route("/cart")
def cart():
    ids=session.get("cart",[])
    items=[]
    if ids:
        with db() as c:
            for pid in ids:
                p=c.execute("SELECT * FROM products WHERE id=? AND active=1",(pid,)).fetchone()
                if p: items.append(p)
    total=sum(p["price"] for p in items)
    return render_template("cart.html",items=items,total=total)

@app.post("/cart/add/<int:pid>")
def add_cart(pid):
    with db() as c: p=c.execute("SELECT id,stock,active FROM products WHERE id=?",(pid,)).fetchone()
    if not p or not p["active"]: abort(404)
    cart=session.get("cart",[])
    cart.append(pid); session["cart"]=cart
    flash("Added to your bag.","success")
    return redirect(request.referrer or url_for("home"))

@app.post("/cart/remove/<int:pid>")
def remove_cart(pid):
    cart=session.get("cart",[])
    try: cart.remove(pid)
    except ValueError: pass
    session["cart"]=cart
    return redirect(url_for("cart"))

@app.post("/checkout")
@customer_required
def checkout():
    ids=session.get("cart",[])
    if not ids:
        flash("Your bag is empty.","warning"); return redirect(url_for("cart"))
    with db() as c:
        rows=[]
        for pid in ids:
            p=c.execute("SELECT * FROM products WHERE id=? AND active=1",(pid,)).fetchone()
            if p: rows.append(p)
        total=sum(p["price"] for p in rows)
        customer=c.execute("SELECT * FROM customers WHERE id=?",(session["customer_id"],)).fetchone()
        summary=[{"product":p["name"],"category":p["category"],"price":p["price"]} for p in rows]
        c.execute("INSERT INTO orders(customer_id,customer_name,email,items_json,total) VALUES(?,?,?,?,?)",
                  (customer["id"],customer["name"],customer["email"],json_dumps(summary),total))
    lines=["Hi Hustle Nation! I would like to place an order:",f"Customer: {customer['name']}",f"Email: {customer['email']}"]
    for item in summary: lines.append(f"- {item['category']} / {item['product']} — R{item['price']}")
    lines.append(f"Estimated total: R{total}"); lines.append("Please confirm sizes, colours, stock and delivery/collection.")
    import urllib.parse
    link="https://wa.me/"+settings().get("whatsapp",WHATSAPP_NUMBER)+"?text="+urllib.parse.quote("\n".join(lines))
    session["cart"]=[]
    return redirect(link)

def json_dumps(obj):
    import json
    return json.dumps(obj)

@app.route("/about")
def about(): return render_template("info.html", title="About Us", content=settings().get("about",""))

@app.route("/terms")
def terms(): return render_template("info.html", title="Terms & Conditions", content=settings().get("terms",""))

@app.route("/gallery")
def gallery():
    with db() as c: photos=c.execute("SELECT * FROM gallery ORDER BY id DESC").fetchall()
    return render_template("gallery.html", photos=photos)

@app.route("/creator", methods=["GET","POST"])
def creator_login():
    if request.method=="POST":
        name=request.form.get("name","").strip()
        phone=request.form.get("phone","").replace(" ","").strip()
        if name.casefold()==ADMIN_NAME.casefold() and phone==ADMIN_PHONE:
            session["admin"]=True; session["admin_name"]=name
            return redirect(url_for("dashboard"))
        flash("Creator name or phone number is incorrect.","error")
    return render_template("creator_login.html")

@app.route("/creator/logout")
def creator_logout():
    session.pop("admin",None); session.pop("admin_name",None)
    return redirect(url_for("home"))

@app.route("/creator/dashboard")
@admin_required
def dashboard():
    with db() as c:
        products=[dict(r) for r in c.execute("SELECT * FROM products ORDER BY category,name").fetchall()]
        orders=c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 30").fetchall()
        photos=c.execute("SELECT * FROM gallery ORDER BY id DESC").fetchall()
    return render_template("dashboard.html", products=products, orders=orders, photos=photos, site=settings(), categories=list(PRICE_LIST.keys()))

@app.post("/creator/product/save")
@admin_required
def save_product():
    f=request.form; pid=f.get("id","").strip()
    try:
        image=save_image(request.files.get("image"))
        data=(f.get("category","").strip(),f.get("name","").strip(),int(f.get("price","0")),
              f.get("description","").strip(),image,f.get("sizes","S, M, L, XL, XXL"),
              f.get("colors","Black, White"),max(0,int(f.get("stock","0"))),1 if f.get("active") else 0)
        if not data[0] or not data[1] or data[2]<0: raise ValueError("Category, product name and a valid price are required.")
        with db() as c:
            if pid:
                if image:
                    c.execute("UPDATE products SET category=?,name=?,price=?,description=?,image=?,sizes=?,colors=?,stock=?,active=? WHERE id=?",data+(int(pid),))
                else:
                    c.execute("UPDATE products SET category=?,name=?,price=?,description=?,sizes=?,colors=?,stock=?,active=? WHERE id=?",
                              (data[0],data[1],data[2],data[3],data[5],data[6],data[7],data[8],int(pid)))
            else:
                c.execute("INSERT INTO products(category,name,price,description,image,sizes,colors,stock,active) VALUES(?,?,?,?,?,?,?,?,?)",data)
        flash("Product saved.","success")
    except Exception as e: flash(str(e),"error")
    return redirect(url_for("dashboard")+"#products")

@app.post("/creator/product/delete/<int:pid>")
@admin_required
def delete_product(pid):
    with db() as c: c.execute("DELETE FROM products WHERE id=?",(pid,))
    flash("Product deleted.","success"); return redirect(url_for("dashboard")+"#products")

@app.post("/creator/gallery")
@admin_required
def upload_gallery():
    try:
        image=save_image(request.files.get("image"))
        if not image: raise ValueError("Choose an image first.")
        with db() as c: c.execute("INSERT INTO gallery(title,image) VALUES(?,?)",(request.form.get("title","Gallery photo"),image))
        flash("Gallery image uploaded.","success")
    except Exception as e: flash(str(e),"error")
    return redirect(url_for("dashboard")+"#gallery")

@app.post("/creator/gallery/delete/<int:gid>")
@admin_required
def delete_gallery(gid):
    with db() as c:
        row=c.execute("SELECT image FROM gallery WHERE id=?",(gid,)).fetchone()
        if row:
            try: (UPLOAD_DIR/row["image"]).unlink(missing_ok=True)
            except Exception: pass
            c.execute("DELETE FROM gallery WHERE id=?",(gid,))
    return redirect(url_for("dashboard")+"#gallery")

@app.post("/creator/settings")
@admin_required
def update_settings():
    fields=["store_name","launch_date","launch_notice","about","terms","theme","loader_theme","maintenance_message","whatsapp","instagram","tiktok","facebook"]
    for key in fields:
        if key in request.form: set_setting(key,request.form.get(key,"").strip())
    if "maintenance" in request.form: set_setting("maintenance","1" if request.form.get("maintenance")=="1" else "0")
    for key in ["logo","loader_logo"]:
        if request.files.get(key) and request.files[key].filename:
            try: set_setting(key,save_image(request.files[key]))
            except Exception as e: flash(str(e),"error")
    flash("Store settings updated.","success")
    return redirect(url_for("dashboard")+"#settings")

@app.post("/api/chat")
def chat():
    message=request.json.get("message","").lower() if request.is_json else ""
    s=settings()
    answers=[
      (("price","cost","how much"),"Our prices are listed on each product page. Choose a category and item to see the price."),
      (("order","buy","checkout","whatsapp"),"Add items to your bag, log in, then choose WhatsApp checkout. Our team will confirm sizes, colours, stock and delivery."),
      (("size","sizes"),"Available sizes are shown on each product. Please confirm your required size with our team on WhatsApp."),
      (("colour","color"),"Product colours are shown on each item. Ask us on WhatsApp to confirm current colour availability."),
      (("delivery","collect","collection"),"Delivery or collection arrangements are confirmed directly with our team on WhatsApp."),
      (("launch","open","opening"),f"Our store launch date is {s.get('launch_date','4 December 2026')}."),
      (("contact","phone","whatsapp"),f"Contact Hustle Nation on WhatsApp: {s.get('whatsapp',WHATSAPP_NUMBER)}.")
    ]
    answer="Welcome to Hustle Nation! I can help with prices, products, sizes, colours, orders and store information. What would you like to know?"
    for words,reply in answers:
        if any(w in message for w in words): answer=reply; break
    return jsonify({"reply":answer})

@app.route("/health")
def health(): return jsonify({"status":"ok","service":"Hustle Nation Store"})

init_db()
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)
