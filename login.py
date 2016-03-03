import webapp2
import cgi
import re
import os
import jinja2
import hmac
import random
import string
import hashlib
import signup

from userModel import User

from google.appengine.ext import db

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

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt=make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return "%s,%s"%(h,salt)

def valid_pw(name,pw,h):
	salt = h.split(',')[1]
	return h == make_pw_hash(name,pw,salt)

class Handler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class LoginHandler(Handler):
	def get(self):
		self.render("login.html")
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		
		if not username:
			self.render("login.html",error="Please enter a username")
		else:
			q = User.all()
			q.filter("username =",username)
			muser = q.get()
			if not muser:
				self.render("login.html",username=username,error="incorrect username or password")
			elif valid_pw(username,password,muser.pwhash):
				userhash = make_user_hash(username)
				self.response.headers.add_header('Set-Cookie', str('user_id=%s; Path=/'% userhash))
				self.redirect("/blog/welcome")
			else:
				self.render("login.html",username=username,error="incorrect username or password")
class LogoutHandler(Handler):
	def get(self):
		#remove cookie, reload login page
		self.response.headers.add_header('Set-Cookie', str('user_id=; Path=/'))
		self.redirect("/blog/signup")