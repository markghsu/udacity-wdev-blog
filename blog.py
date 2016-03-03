import webapp2
import json
import datetime
import time
from google.appengine.api import memcache

from handlerparent import Handler
from google.appengine.ext import db

def getPosts(update=False):
	posts = memcache.get('top')
	if update or not posts:
		posts = (db.GqlQuery("SELECT * FROM Post ORDER BY created DESC"), time.time())
		memcache.add('top',posts,100)
	return posts
def getPost(pid, update=False):
	post = memcache.get(pid)
	if update or not post:
		post = (Post.get_by_id(int(pid)),time.time())
		memcache.add(pid,post,100)
	return post
def flushCache():
	memcache.flush_all()

class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	modified = db.DateTimeProperty(auto_now = True)

	def render(self):
		self._content = self.content.replace('\n', '<br>')
		return render_str("blogpost.html",subject=self.subject,content=self._content)

class BlogHandler(Handler):
	def get(self):
		gp = getPosts()
		self.render("front.html",posts=gp[0],time='%.4f'%(time.time()-gp[1]))
class FlushHandler(Handler):
	def get(self):
		flushCache()
		self.redirect("/blog")

class PostHandler(Handler):
	def get(self, pid):
		gp = getPost(pid)
		if gp:
			self.render("blogpost.html",post=gp[0],time='%.4f'%(time.time()-gp[1]))
		else:
			self.error(404)
			return
			#self.response.write('Error')

class NewHandler(Handler):
	def write_form(self,subject="",content="",error=""):
		self.render("blognew.html",subject=subject,content=content,error=error)
	def get(self):
		self.write_form()
	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')
		if not subject:
			self.write_form(subject="",content=content,error="Error, subject required")
		elif not content:
			self.write_form(subject=subject,content="",error="Error, content required")
		else:
			p = Post(subject=subject,content=content)
			p.put()
			flushCache()
			self.redirect("/blog/"+str(p.key().id()))

class JSONHandler(webapp2.RequestHandler):
	def get(self):
		pout = []
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
		posts = list(posts)
		for p in posts:
			self.response.headers['Content-Type'] = 'application/json'
			pout.append({"content":p.content, "created":p.created.isoformat(' '),"last_modified":p.modified.isoformat(' '),"subject":p.subject})
		self.response.out.write(json.dumps(pout))

class PostJSONHandler(webapp2.RequestHandler):
	def get(self, pid):
		p = Post.get_by_id(int(pid))
		if p:
			self.response.headers['Content-Type'] = 'application/json'
			mdict = {"content":p.content, "created":p.created.isoformat(' '),"last_modified":p.modified.isoformat(' '),"subject":p.subject}
			self.response.out.write(json.dumps(mdict))
		else:
			self.error(404)
			return
			#self.response.write('Error')