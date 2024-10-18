


class manipuleer_filename():
    def __init__(self):
        self.filename = "originele_filename.pdf"
        #self. referereert naar de class self, dus self.variable geeft aan dat variable een attribute van de class is
        pass #pass betekend niks doen en doorgaan

    def set_filename(self,filename):#methode/functie van de class
        self.filename = filename
        #nu is filename opgeslagen in de class onder attribute self.filename
        pass #weer doorgaan

    def get_filename(self):
        return self.filename #return de waarde van de filename
    

if __name__ == "__main__":#code uitvoeren als we deze file runnen

    x = manipuleer_filename()
    print(x.filename)
    print(x.get_filename())
    #bovenstaande twee lijnen code laten beide de waarde van filename zien
    x.set_filename("nieuwe_filename.pdf")#nieuwe filename setten
    print(x.get_filename())#gemodificeerde filename getten
