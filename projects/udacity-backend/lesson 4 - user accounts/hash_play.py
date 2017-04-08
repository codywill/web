import hashlib
import hmac
import random
import string

#def hash_str(s):
#    return hashlib.md5(s).hexdigest()

# -----------------
# User Instructions
# 
# Implement the function make_secure_val, which takes a string and returns a 
# string of the format: 
# s,HASH

def make_secure_val(s):
    return "%s,%s" % (s, hash_str(s))

# Implement the function check_secure_val, which takes a string of the format 
# s,HASH
# and returns s if hash_str(s) == HASH, otherwise None 

def check_secure_val(h):
    n = h.split(",")[0]
    if h == make_secure_val(n):
        return n
        
# Implement the hash_str function to use HMAC and our SECRET instead of md5
SECRET = 'imsosecret'
def hash_str(s):
    return hmac.new(SECRET,s).hexdigest()
    
# implement the function make_salt() that returns a string of 5 random
# letters use python's random module.
# Note: The string package might be useful here.

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

# implement the function make_pw_hash(name, pw) that returns a hashed password 
# of the format: 
# HASH(name + pw + salt),salt
# use sha256

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    return "%s,%s" % (hashlib.sha256(name + pw + salt).hexdigest(), salt)

# Implement the function valid_pw() that returns True if a user's password 
# matches its hash. You will need to modify make_pw_hash.

def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)

