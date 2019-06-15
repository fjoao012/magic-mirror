# magic-mirror
Magic mirror application

# Pre-requisites
- Install python3 (NOT python2!!!!) on your machine
- (Optional) Install an IDE like PyCharm Community Edition

# Usage
0) (Linux) Run run apt install python3-tk python3-pil python3-pil.imagetk
1) Install the required packages: pip install -r requirements.txt
2) Run the application: python3 magic-mirror.py

# FAQ
Q1) I can't run magic-mirror.py, because of some 'tkinter' library not being found...
A1) Linux: ensure you have ran Step 0)
	-> sudo apt install python3-tk
	
	Linux/Windows: pip3 install tkinter
	If that doesn't work -> you might have a slightly bigger problem :)
	
Q2) I can't run magic-mirror.py, because python3 can't seem to import 'ImageTk'... 
A2) Linux: ensure you have ran Step 0)
	-> sudo apt install python3-pil python3-pil.imagetk
