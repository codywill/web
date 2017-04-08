import os
import re
import hmac
import hashlib
import random
import webapp2
import jinja2
from string import letters
from google.appengine.ext import db
SECRET = 'secretkey'

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
                               
def render_str(template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

def make_secure_val(s):
    return "%s|%s" % (s, hmac.new(SECRET, s).hexdigest())

def check_secure_val(h):
    n = h.split("|")[0]
    if h == make_secure_val(n):
        return n                               

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (salt, h)

def valid_pw(name, pw, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, pw, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)
    
class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()
    
    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())
        
    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u
        
    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)
                    
    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
    
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))
    
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
    
class Content(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class MainPage(Handler):
    def render_front(self, subject="", content="", error=""):
        content = db.GqlQuery("select * from Content order by created desc")
        self.render("front.html", subject=subject, content=content)
        
    def get(self):
        self.render_front()

class NewPost(Handler):
    def render_new(self, subject="", content="", error=""):
        self.render("newpost.html", subject=subject, content=content, error=error)
    
    def get(self):
        self.render_new()
    
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        
        if subject and content:
            c = Content(subject=subject, content=content)
            c.put()
            
            self.redirect("/")
        else:
            error = "please include a subject and some content"
            self.render_new(subject, content, error)
            
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Register(Handler):
    def get(self):
        self.render("signup.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup.html', **params)
        else:
            # username_secure = make_secure_val(str(username))
            # self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % username_secure)
            # self.redirect('/welcome')
            self.done()
            
    def done(self, *a, **kw):
        raise NotImplementedError
        
class Signup(Register):
    def done(self):
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()
            self.login(u)
            self.redirect('/welcome')
            
class Welcome(Handler):
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
        else:
            self.redirect('/signup')
            
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/newpost', NewPost),
                               ('/signup', Signup),
                               ('/welcome', Welcome)], debug=True)