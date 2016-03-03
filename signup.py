import webapp2
import cgi
import re
import os
import jinja2
import hmac
import random
import string
import hashlib

from userModel import User

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

SECRET = 'm2Sno31xz'
def user_hash(s):
	return hmac.new(SECRET,s).hexdigest()

def make_user_hash(s):
	return "%s|%s" % (s, user_hash(s))

def check_user_hash(h):
	val = h.split('|')[0]
	if h == make_user_hash(val):
		return val

def make_salt():
		return ''.join(random.choice(string.letters) for x in xrange(7))

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt=make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return "%s,%s"%(h,salt)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def error_username(username):
	q = User.all()
	q.filter("username =",username)
	dup = q.get()
	if not USER_RE.match(username):
		return "That's not a valid username."
	elif dup:
		return "That username is taken."
	else:
		return ""

PASS_RE = re.compile(r"^.{3,20}$")
def error_password(st):
	if not PASS_RE.match(st):
		return "That wasn't a valid password."
	else:
		return ""


EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def error_email(st):
	if st:
		if not EMAIL_RE.match(st):
			return "That's not a valid email."
		else:
			return ""
	else:
		return ""
class Handler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class SignupHandler(Handler):
	def get(self):
		self.render("signup.html")
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')
		ue = error_username(username)
		pe = error_password(password)
		ve = "Your passwords didn't match." if password!=verify else ""
		ee = error_email(email)

		if not (ue or pe or ve or ee):
			userhash = make_user_hash(username)
			passhash = make_pw_hash(username,password)
			muser = User(username=username,pwhash=passhash)
			muser.put()
			
			#add to DB and set login cookie
			self.response.headers.add_header('Set-Cookie', str('user_id=%s; Path=/'% userhash))
			self.redirect("/blog/welcome")
		else:
			self.render("signup.html",username=username,uerror=ue,perror=pe,verror=ve,email=email,eerror=ee)

class WelcomeHandler(Handler):
	def get(self):
		user_id = self.request.cookies.get('user_id')
		username = check_user_hash(user_id)

		if username:
			self.response.out.write("Welcome, "+username)
		else:
			self.redirect("/blog/signup")