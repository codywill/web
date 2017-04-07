import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Content(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)

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
            
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/newpost', NewPost)], debug=True)