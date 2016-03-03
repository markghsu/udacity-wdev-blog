import webapp2
import rot13
import signup
import templ
import blog
import login

form = """
<form method="post" action="test">
	<group>
		<label>A
			<input type="radio" name="r" value="a">
		</label>
		<input type="radio" name="r" value="b">
		<input type="radio" name="r" value="c">
	</group>
	<select name="drop">
		<option>one</option>
		<option value="abc">two</option>
	</select>
	What is your birthday?
	<input name="month" type="text">
	<input name="day" type="text">
	<input name="year" type="text">
	<div style="color: red">%(error)s</div>
	<input type="submit">
</form>"""
class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write("test")
	def write_form(self,error="",month="",day="",year=""):
		self.response.out.write(form%{"error": error,"month":month, "day":day,"year":year})
	def post(self):
		self.response.out.write("bye")
		
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rot13', rot13.Rot13Handler),
    ('/blog/signup', signup.SignupHandler),
    ('/blog/welcome', signup.WelcomeHandler),
    ('/temp', templ.tHandler),
    ('/blog', blog.BlogHandler),
    ('/blog/(\d+)',blog.PostHandler),
    ('/blog/newpost',blog.NewHandler),
    ('/blog/login', login.LoginHandler),
    ('/blog/logout', login.LogoutHandler),
    ('/blog/\.json', blog.JSONHandler),
    ('/blog/(\d+)\.json',blog.PostJSONHandler),
    ('/blog/flush',blog.FlushHandler)
], debug=True)
