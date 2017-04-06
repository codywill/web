import os
import cgi
import webapp2

form="""
<form method="post">
	<h2>Rot13 Cipher Converter</h2>
    Enter some text:
	<br>
	<textarea name="text" rows="4" cols="50">%(text)s</textarea>
	<br><br>
	<button>Convert</button>
</form>
"""

def escape_html(s):
    return cgi.escape(s, quote = True)

def rot13_convert(text):
    if text:
        newtext=''
        for ch in text:
            if ord(ch.lower()) <= ord('m') and ord(ch.lower()) >= ord('a'):
                newch = chr(ord(ch)+13)
            elif ord(ch.lower()) <= ord('z') and ord(ch.lower()) >= ord('n'):
                newch = chr(ord(ch)-13)
            else:
                newch = ch
            newtext+=newtext.join(newch)
        return newtext
    else:
        return ''

class MainPage(webapp2.RequestHandler):
    def write_form(self, text=""):
        self.response.out.write(form % {"text":text})
        
    def get(self):
        self.write_form()
    
    def post(self):
        text = self.request.get('text')
        self.write_form(escape_html(rot13_convert(text)))
        
app = webapp2.WSGIApplication([('/', MainPage),
                               ],
							   debug=True)