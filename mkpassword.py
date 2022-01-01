#!/usr/bin/python3
import sys, crypt # Import the needed library 
if len(sys.argv) == 1 : sys.exit("You must supply the password!") # error checking if there is no string provided
print(crypt.crypt(sys.argv[1], crypt.mksalt(crypt.METHOD_SHA512))) # crypt and salt the second item in the list aka the password string.
