import tkinter as tk

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()

class Page1(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        minDisp = tk.IntVar()
        scale = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=0, to=100, tickinterval=10, resolution=5, variable=minDisp, label="minDisp")
        scale.pack()

        numDisp = tk.IntVar()
        scale2 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=2.0, to=160, tickinterval=10, resolution=16, variable=numDisp, label="numDisp")
        scale2.pack()

        blockSize = tk.IntVar()
        scale3 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=3, to=25, tickinterval=10, resolution=2, variable=blockSize, label="blockSize")
        scale3.pack()

        speckleWindowSize  = tk.IntVar()
        scale4 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=1, to=100, tickinterval=10, resolution=5, variable=speckleWindowSize, label="speckleWindowSize" )
        scale4.pack()

        speckleRange  = tk.IntVar()
        scale5 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=0, to=250, tickinterval=25, resolution=5, variable=speckleRange , label="speckleRange")
        scale5.pack()

        disp12MaxDiff  = tk.IntVar()
        scale6 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=0, to=10, tickinterval=10, resolution=1, variable=disp12MaxDiff , label="disp12MaxDiff")
        scale6.pack()
        
        
        button = tk.Button(self, text = "Set the Values")
        button.pack()
    def getValues():
        return(minDisp.get(), numDisp.get(), blockSize.get(), speckleWindowSize.get(), speckleRange.get(), disp12MaxDiff.get())


class Page2(Page):
   def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        sigma = tk.DoubleVar()
        scale = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=0.8, to=2.0, tickinterval=0.4, resolution=0.2, variable=sigma, label="Sigma")
        scale.pack()

        lmbda = tk.IntVar()
        scale2 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=8000, to=80000, tickinterval=20000, resolution=1000, variable=lmbda, label="Lambda")
        scale2.pack()

        button = tk.Button(self, text = "Set the Values")
        button.pack()
    def getValues():
        return(sigma.get(), lmbda.get())



class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        p1 = Page1(self)
        p2 = Page2(self)

        buttonframe = tk.Frame(self)
        container = tk.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        val1, val2,val3,val4,val5,val6,val7,val8 = p1.getValues(), p2.getValues()
        set_values_loaded = partial(setValues, val1, val2, val3, val4, val5, val6, val7, val8)

        b1 = tk.Button(buttonframe, text="SGMB", command=p1.lift)
        b2 = tk.Button(buttonframe, text="Matcher", command=p2.lift)
        b3 = tk.Button(buttonframe, text="Apply values", command=set_values_loaded)


        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="right")

        p1.show()

if __name__ == "__main__":
   root = tk.Tk()
   main = MainView(root)
   main.pack(side="top", fill="both", expand=True)
   root.wm_geometry("400x800")
   root.mainloop()