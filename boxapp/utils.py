import jwt

A1 = 100
V1 = 1000
L1 = 100
L2 = 50

# Function to check if access token is valid or not
def authenticate(token):
    try:
        payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        return True
    except:
        return False
