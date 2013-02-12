import Tkinter
import os
import webbrowser
try:
	 import contextminer
	 installed = True
except ImportError, e:
	 installed = False

print installed

#button=Tkinter.Button()
#button2=Tkinter.Button()
#button3=Tkinter.Button()
#button4=Tkinter.Button()

class simpleapp_tk(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()
	def initialize(self):
		self.grid()
		self.entry = Tkinter.Entry(self)
		self.entry.bind("<Return>", self.OnPressEnter)
		
		#button = Tkinter.Button(self,text="Install",
		#command=self.OnButtonClick)
		#button.grid(column=0,row=1)
		self.button2 = Tkinter.Button(self,text='Cmstart',
		command=self.OnSecondButtonClick,
		state='disabled')
		self.button2.grid(column=1,row=1)	

		self.button3 = Tkinter.Button(self,text='Cmstop',
		command=self.OnThirdButtonClick,
		state='disabled')
		self.button3.grid(column=2,row=1)
	
		self.button4=Tkinter.Button(self, text='Launch Browser',
		command=self.launchBrowser,
		state='disabled')
		self.button4.grid(column=3,row=1)

		self.button = Tkinter.Button(self, text="Install",
		command = self.OnButtonClick)
		self.button.grid(column=0, row=1)

		self.grid_columnconfigure(0,weight=2)
		self.resizable(True,False)
		if installed:
			self.setAllVisible()
	def OnButtonClick(self):
		os.system("bash install_cm")
		self.setAllVisible()
	def OnSecondButtonClick(self):
		os.system("sudo cmstart")
	def OnThirdButtonClick(self):
		os.system("sudo cmstop")
	def launchBrowser(self):
		webbrowser.open('localhost:5000')
	def OnPressEnter(self,event):
		self.labelVariable.set("You pressed enter !")
	def setAllVisible(self):
		self.button.config(state='disabled')
		self.button2.config(state='active')
		self.button3.config(state='active')
		self.button4.config(state='active')
if __name__ == "__main__":
	app = simpleapp_tk(None)
	app.title('Contextminer')
	app.mainloop()
