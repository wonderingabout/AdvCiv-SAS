# <!-- custom: modified from Claude AI's (kindly shared (to me or and all or not or and othe ror and not but anyways etc anyways etc anyways etc...)) or not for AdvCiv-SAS or/and my personal taste or feel or/and wish or thought or and other or and not anyways etc anyways etc anyways etc... -->

# Get all attributes of the object
def printObjAttrs(obj):
    for attr in dir(obj):
        try:
            # Try to get the attribute
            attr_value = getattr(obj, attr)
            
            # Check if it's a method (callable)
            if callable(attr_value):
                print(u"%s\n" % attr)
            else:
                print(u"%s = %s\n" % (attr, attr_value))
        except:
            print(u"%s - Error accessing\n" % attr)
