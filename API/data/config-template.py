import sys

DEBUG = True  # Wenn True, werden z.B. eingehende requests geloggt

IS_LOCAL = sys.platform == 'win32'  # Wenn ihr Linux nutzt, müsst ihr das natürlich anpassen/manuel auf True setzen

if IS_LOCAL:
    HOST, PORT = 'localhost', 6969
else:
    HOST, PORT = 'devsky.one', 0  # TODO: Auf welchem Endpoint läuft die API?
