import webapp2
import cgi
h="""<h2>Enter some text to ROT13:</h2>"""
form = """
<form method="post">
	<textarea name="text" style="height: 100px; width: 400px;">%(text)s</textarea>
	<br/>
	<input type="submit">
</form>"""

def r13(s):
	l = list()
	for char in s:
		if char.isalpha():
			num = ord(char)
			if num <= 77 or num >=97 and num <=109:
				num+=13
			else:
				num-=13
			char=str(unichr(num))
		l+=char
	return "".join(l)

class Rot13Handler(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		self.write_form()
	def write_form(self,txt=""):
		self.response.out.write(h)
		self.response.out.write(form%{"text": cgi.escape(txt, quote=True)})
	def post(self):
		t = self.request.get('text')
		self.write_form(r13(t))