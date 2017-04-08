import hashlib
import hmac

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