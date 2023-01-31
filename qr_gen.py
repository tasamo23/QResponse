import qr_ecc as ecc

class QRCode:
    def chooseMask():
        # Let the program choose the preferred mask by evaluating group size
        # and avoidung misleading patterns
    def insertStaticMarkers():
        # Insert the locator patterns and markers
    def insertMetaData():
        # Insert version, ecc mode and pattern data into the code
    def insertData():
        # Insert the message into the code

    def generate():
        insertStaticMarkers();
        insertMetaData();
        insertData();
        chooseMask();