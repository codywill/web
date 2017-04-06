import os
import cgi
import webapp2
import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PW_RE = re.compile(r"^.{3,20}$")
VERIFY_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")
GLOBAL_USER = ""

form="""
<form method="post">
	<h2>Sign up</h2>
	<div style="float: left; width: 300px" align="right"> 
		<label>
			Username <input type="text" name="username" value="%(username)s">
		</label>
	</div>
	<span align="left" style="color:red; width: 200px">
		&nbsp;%(user_error)s
	</span>
	<br><br>
	<div style="float: left; width: 300px" align="right"> 
		<label>
			Password <input type="password" name="password" value="%(password)s">
		</label>
	</div>
	<span align="left" style="color:red; width: 200px">
		&nbsp;%(password_error)s
	</span>
	<br><br>
	<div style="float: left; width: 300px" align="right"> 
		<label>
			Verify Password <input type="password" name="verify" value="%(verify)s">
		</label>
	</div>
	<span align="left" style="color:red; width: 200px">
		&nbsp;%(verify_error)s
	</span>
	<br><br>
	<div style="float: left; width: 300px" align="right"> 
		<label>
			Email (optional) <input type="text" name="email" value="%(email)s">
		</label>
	</div>
	<span align="left" style="color:red; width: 200px">
		&nbsp;%(email_error)s
	</span>
	<br><br><br>
	<input type="submit">
</form>
"""

def escape_html(s):
	return cgi.escape(s, quote = True)

def valid_username(username):
	return USER_RE.match(username)

def valid_password(password):
	return PW_RE.match(password)

def valid_verify(verify):
	return VERIFY_RE.match(verify)
	
def valid_email(email):
	return EMAIL_RE.match(email)

class MainPage(webapp2.RequestHandler):
	def write_form(self, user_error="", password_error="", verify_error="", email_error="",
						 username="", password="", verify="", email=""):
		
		self.response.out.write(form % {"user_error": user_error,
										"password_error": password_error,
										"verify_error": verify_error,
										"email_error": email_error,
										"username": escape_html(username),
										"password": escape_html(password),
										"verify": escape_html(verify),
										"email": escape_html(email)})
	
	def get(self):
		self.write_form()
	
	def post(self):
		global GLOBAL_USER
		in_username = self.request.get('username')
		in_password = self.request.get('password')
		in_verify = self.request.get('verify')
		in_email = self.request.get('email')
		
		GLOBAL_USER = in_username
		
		username = valid_username(in_username)
		password = valid_password(in_password)
		verify = valid_verify(in_verify)
		email = valid_email(in_email)
		
		if not(username):
			user_error = "Invalid user name"
			# self.write_form("Invalid user name", password_error, verify_error, email_error,
							# in_username, in_password, in_verify, in_email)
		else:
			user_error = ""
		if not(password):
			password_error = "Invalid password"
			# self.write_form(user_error, "Invalid password", verify_error, email_error,
							# in_username, in_password, in_verify, in_email)
		else:
			password_error = ""
		if not(verify and in_verify == in_password):
			verify_error = "Passwords do not match"
			# self.write_form(user_error, password_error, "Passwords do not match", email_error,
							# in_username, in_password, in_verify, in_email)
		else:
			verify_error = ""
		if not(email or email == ""):
			email_error = "Invalid email"
			# self.write_form(user_error, password_error, verify_error, "Invalid email",
							# in_username, in_password, in_verify, in_email)
		else:
			email_error = ""
		if not(username and password and verify and in_verify == in_password):
			self.write_form(user_error, password_error, verify_error, email_error,
							in_username, in_password, in_verify, in_email)
		else:
			self.redirect("/welcome")

class WelcomeHandler(webapp2.RequestHandler):
	global GLOBAL_USER
	def get(self):
		self.response.out.write("Welcome, %s" % GLOBAL_USER)

app = webapp2.WSGIApplication([('/', MainPage),('/welcome', WelcomeHandler)], debug=True)