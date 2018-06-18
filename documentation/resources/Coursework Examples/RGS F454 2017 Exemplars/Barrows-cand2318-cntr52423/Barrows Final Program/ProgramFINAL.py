import sys, os, time, uuid, hashlib, re                 #importing libraries (system, operating system, hashing functions, regex)
from PyQt4 import QtCore, QtGui, uic, QtSql             #importing relevant PyQt4 modules
import sqlite3 as lite                                  #importing library to connect to SQLite database
con = lite.connect('PizzaDatabase.db')                  #Connecting to database
cur = con.cursor()                                      #Setting cursor of database

win2 = uic.loadUiType("LogIn.ui") [0]                   #Loading all required GUIs
win3 = uic.loadUiType("CustomerDetails.ui") [0]
win4 = uic.loadUiType("PizzaOrder.ui") [0]
win5 = uic.loadUiType("OrderConfirmation.ui") [0]
win8 = uic.loadUiType("ViewOrdersScreen.ui") [0]
win9 = uic.loadUiType("OrderView.ui") [0]
win10 = uic.loadUiType("ViewUserOrders.ui") [0]
win11 = uic.loadUiType("UserOrder.ui") [0]
win12 = uic.loadUiType("DetailsAccepted.ui") [0]
win13 = uic.loadUiType("UpdateDetails.ui") [0]
win14 = uic.loadUiType("AdminScreen.ui") [0]
win15 = uic.loadUiType("ViewAllDetails.ui") [0]
win16 = uic.loadUiType("PasswordRecovery.ui") [0]
win17 = uic.loadUiType("DataAnalytics.ui") [0]
win18 = uic.loadUiType("PostcodeChecker.ui") [0]

class SecondWindow(QtGui.QMainWindow, win2):            #loads the login window
    def __init__(self, parent=None):                    #initialising the window (constructor)
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)                              #Setting up the UI
        self.loginbutton.clicked.connect(self.login)    #Defining what happens when each button is pressed
        self.PassWord.returnPressed.connect(self.login)
        self.signupbutton.clicked.connect(self.signup)
        self.forgot.clicked.connect(self.forgotpass)
    def signup(self):                                   #Sign Up function - activated when "Sign Up" button pressed
        self.signupwindow = ThirdWindow()
        self.signupwindow.show()
        self.hide()
    def verifyhash(self, userpass, storedpass):         #Verifies the hash
        self.userpass = userpass
        try:                                            #Prevents crash in instance of invalid stored hash
            password,salt=storedpass.split(":")
        except:
            pass
        else:
            data = []
            data.append(password)
            data.append(hashlib.sha256(salt.encode()+self.userpass.encode()).hexdigest())
            return data[0]==data[1]
    def login(self):                                    #Login function
        global usernameoptionsid
        usernameoptionsid=""
        usernameoptions=""
        usernameattempt = self.UserName.text()
        passwordattempt = self.PassWord.text()
        if usernameattempt == "":
            self.hide()
            self.Order2= SecondWindow()
            self.Order2.show()
            QtGui.QMessageBox.information(self, "Incorrect Details", "Your username/password is incorrect. \n Please try again...")
        else:
            usernamesql = """SELECT "UserName" FROM "CustomerInformation" WHERE "UserName" = '%s' """ % (usernameattempt)
            cur.execute(usernamesql)
            usernameoptions = cur.fetchall()
            username2sql = """SELECT "CustomerID" FROM "CustomerInformation" WHERE "UserName" = '%s' """ % (usernameattempt)
            cur.execute(username2sql)
            usernameoptionjj = cur.fetchall()
            usernameoptionsid = usernameoptionjj
            try:
                passwordsql = """SELECT "Password" FROM "CustomerInformation" WHERE "CustomerID" = '%d' """ % (usernameoptionsid[0])
                cur.execute(passwordsql)
                passwordoptions = cur.fetchall()
            except:
                self.hide()
                self.Order2= SecondWindow()
                self.Order2.show()
                QtGui.QMessageBox.information(self, "Incorrect Details", "Your username/password is incorrect. \n Please try again...")
            else:
                if self.verifyhash(passwordattempt, passwordoptions[0][0]): #Compares inputted password and the stored password
                    self.hide()
                    accountypesql = """SELECT "AccountType", "AccountStatus" FROM "CustomerInformation" WHERE "CustomerID" = '%d' """ % (usernameoptionsid[0])
                    cur.execute(accountypesql)
                    accounttype = cur.fetchall()
                    if accounttype[0][1] == "Active":
                        if accounttype[0][0] == "Customer":     #Opens the appropiate window based on the account type of the user
                            self.Order = TenthWindow()
                            self.Order.show()
                        elif accounttype[0][0] == "Staff":
                            self.Order = EighthWindow()
                            self.Order.show()
                        elif accounttype[0][0] == "Admin":
                            self.Order = FourteenthWindow()
                            self.Order.show()
                    else:                                       #If account is not active, the useris denied access
                        self.Order2= SecondWindow()
                        self.Order2.show()
                        QtGui.QMessageBox.information(self, "Account Suspended", "This account has been suspended. \n Contact the system administrator.")
                else:
                    self.hide()
                    self.Order2= SecondWindow()
                    self.Order2.show()
                    QtGui.QMessageBox.information(self, "Incorrect Details", "Your username/password is incorrect. \n Please try again...")
    def forgotpass(self):  #Function activated when Forgot Password button clicked
        self.hide()
        self.newwindow=SixteenthWindow()
        self.newwindow.show()
        
class ThirdWindow(QtGui.QMainWindow, win3):                     #Loads sign up window
    def __init__(self, parent=None):                            #Initialises window
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)
        self.CDOrderDone.clicked.connect(self.submit)           #Controls buttons
        self.CDCancel.clicked.connect(self.cancel)
        self.verifypostcode.clicked.connect(self.verify)
        global verifiedpostcode
        verifiedpostcode=False
    def verify(self):                                           #Function to verify the postcode entered
        postcodebox2 = self.Postcode.text()
        postcoderule = re.compile(r'^([A-PR-UWYZ0-9][A-HK-Y0-9][AEHMNPRTVXY0-9]?[ABEHMNPRVWXY0-9]? {1,2}[0-9][ABD-HJLN-UW-Z]{2}|GIR 0AA)$')
        if not postcoderule.search(postcodebox2):
            QtGui.QMessageBox.information(self, "Error!", "Invalid Postcode \n Must be in format: 'XX12 3XX'")   #Validation using REGEX
        else:
            global postcodetoverify
            postcodetoverify=postcodebox2
            self.homescreen = EighteenthWindow()
            self.homescreen.show()
    def submit(self):
        firstnamebox = self.FirstName.text()            #Store data from each input box
        surnamebox = self.Surname.text()
        housenumberbox = self.HouseNumber.text()
        postcodebox = self.Postcode.text()
        mobilenumberbox = self.MobileNumber.text()
        deliverybox = self.PaymentMethod.currentText()
        usernamebox = self.Username.text()
        passwordbox = self.Password.text()
        hashedpass = hasher(passwordbox)
        question = self.questionbox.currentText()
        answer = self.answerbox.text()
        query = QtSql.QSqlQuery()
        if firstnamebox == "" or surnamebox == "" or housenumberbox == 0 or postcodebox == "" or mobilenumberbox == "" or deliverybox == "" or usernamebox == "" or passwordbox == "" or question == "" or answer == "":
            QtGui.QMessageBox.information(self, "Error!", "Some details have been left blank. \n Please check your information...")
        else:
            namerule = re.compile(r'^[a-zA-Z]+$')         #Validation of customer name using REGEX
            if not namerule.search(firstnamebox + surnamebox):
                QtGui.QMessageBox.information(self, "Error!", "Invalid Name \n Can only contain letters")
            else:
                postcoderule = re.compile(r'^([A-PR-UWYZ0-9][A-HK-Y0-9][AEHMNPRTVXY0-9]?[ABEHMNPRVWXY0-9]? {1,2}[0-9][ABD-HJLN-UW-Z]{2}|GIR 0AA)$')
                if not postcoderule.search(postcodebox):   #Validation of postcode using REGEX
                        QtGui.QMessageBox.information(self, "Error!", "Invalid Postcode \n Must be in format: 'XX12 3XX'")
                else:
                    mobilerule = re.compile(r'^(07\d{9,9})$')   #Validation of mobile number using REGEX
                    if not mobilerule.search(mobilenumberbox):
                        QtGui.QMessageBox.information(self, "Error!", "Invalid Mobile Number \n Can only contain 11 numbers, starting with '07'")                  
                    else:
                        checkusername = """SELECT "UserName" FROM "CustomerInformation" """
                        cur.execute(checkusername)
                        allnames = cur.fetchall()
                        used = False
                        for each in allnames:
                            if usernamebox== each[0]:       #This stops a username being used twice
                                QtGui.QMessageBox.information(self, "Error!", "This username is already in use. \n Please choose another...")
                                used = True
                        if used == False:
                            if len(passwordbox) <6:        #Validation of password
                                QtGui.QMessageBox.information(self, "Error!", "Password must contain at least 6 characters!")
                            else:
                                if verifiedpostcode==False:    #Ensures postcode has been verified
                                    QtGui.QMessageBox.information(self, "Error!", "You need to verify your postcode first!")
                                else:
                                    try:
                                        if postcodetoverify==postcodebox:
                                            self.Order = TwelthWindow()
                                            self.Order.show()
                                            sql2 = """SELECT "CustomerID" FROM "CustomerInformation" ORDER BY CustomerID DESC LIMIT 1 """
                                            cur.execute(sql2)
                                            response = 0
                                            response = cur.fetchone()
                                            newcustid = response[0] + 1
                                            query = QtSql.QSqlQuery()      #Input user data into database
                                            sql = """INSERT INTO "CustomerInformation" ("CustomerID", "FirstName", "Surname", "HouseNumber", "Postcode", "MobileNumber", "DeliveryType", "UserName", "Password", "AccountType", "AccountStatus", "SecurityQuestion", "SecurityAnswer") VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, "Customer", "Active", ?, ?)"""
                                            cur.execute(sql, (newcustid, firstnamebox, surnamebox, housenumberbox, postcodebox, mobilenumberbox, deliverybox, usernamebox, hashedpass, question, answer, ))
                                            con.commit()
                                            sqlname = """SELECT "FirstName" FROM CustomerInformation WHERE CustomerID = '%d'""" % (newcustid)
                                            global firstnamereq
                                            cur.execute(sqlname)
                                            firstnamereq = cur.fetchone()
                                            self.hide()
                                        else:
                                            QtGui.QMessageBox.information(self, "Error!", "The current postcode entered is different to the verified one!")
                                    except:
                                        QtGui.QMessageBox.information(self, "Error!", "You need to verify your postcode first!")                
    def cancel(self):
        self.hide()
        self.homescreen = SecondWindow()
        self.homescreen.show()
    
global secondorder
secondorder = False

class FourthWindow(QtGui.QMainWindow, win4):    #GUI to order pizza
    def __init__(self, parent=None):            #Initialises window
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)
        self.POCancel.clicked.connect(self.cancel)
        self.POOrderDone.clicked.connect(self.orderdone)
        self.POAddAnother.clicked.connect(self.another)
        global usernameoptionsid
        sqlname = """SELECT "FirstName" FROM CustomerInformation WHERE CustomerID = '%d'""" % (usernameoptionsid[0])  #Fetches the logged in users name
        global firstnamereq
        cur.execute(sqlname)
        firstnamereq = cur.fetchone()
        self.NameBox.setPlainText(firstnamereq[0])    #Displays the users name in the GUI
    def cancel(self):
        self.hide()
        self.homescreen = TenthWindow()
        self.homescreen.show()
    def orderdone(self):
        global secondorder
        sizebox = self.Size.currentIndex()       #Takes order inputs from GUI
        crustbox = self.StuffedCrust.currentIndex()
        toppingbox = self.Topping.currentIndex()
        extrasbox = self.Extras.currentIndex()
        drinksbox = self.Drink.currentIndex()
        oktogo=True
        if sizebox==0 and crustbox==0 and toppingbox==0 and extrasbox==0 and drinksbox==0:          #Validation stopping empty order
            QtGui.QMessageBox.information(self, "Error!", "You have not chosen anything to order!")
            oktogo=False
        if sizebox > 0 or crustbox > 0 or toppingbox > 0:
            if sizebox==0 or crustbox == 0 or toppingbox == 0: #Ensures that an order is complete before submitting
                QtGui.QMessageBox.information(self, "Error!", "You must choose the Size, Crust Type and Topping if you are ordering pizza.")
                oktogo=False
        if oktogo==True:
            sql2 = """SELECT "ProductLineID" FROM "ProductLine" ORDER BY ProductLineID DESC LIMIT 1 """
            cur.execute(sql2)
            response = 0
            response = cur.fetchone()
            newproductid = response[0] + 1
            sql4 = """SELECT "OrderID" FROM "ProductLine" ORDER BY OrderID DESC LIMIT 1 """
            cur.execute(sql4)
            response1 = 0
            response1 = cur.fetchone()
            if secondorder == True:
                neworderid = response1[0]
            else:
                neworderid = response1[0] + 1
                secondorder = True           
            query = QtSql.QSqlQuery()  #Inserts ordered items into database 'ProductLine' table
            sql = """INSERT INTO "ProductLine" ("ProductLineID", "OrderID", "SizeID", "CrustID", "ToppingID", "ExtrasID", "DrinkID" ) VALUES ( ?, ?, ?, ?,  ?, ?, ?)"""
            cur.execute(sql, (newproductid, neworderid, sizebox, crustbox, toppingbox, extrasbox, drinksbox, ))
            con.commit()
            self.hide()
            self.done = FifthWindow()
            self.done.show()
    def another(self):   #This function is run if the user wants to order more than one pizza
        global secondorder
        sizebox = self.Size.currentIndex()
        crustbox = self.StuffedCrust.currentIndex()
        toppingbox = self.Topping.currentIndex()
        extrasbox = self.Extras.currentIndex()
        drinksbox = self.Drink.currentIndex()
        oktogo=True
        if sizebox==0 and crustbox==0 and toppingbox==0 and extrasbox==0 and drinksbox==0:  #This validates the order to ensure something has been entered
            QtGui.QMessageBox.information(self, "Error!", "You have not chosen anything to order!")
            oktogo=False
        if sizebox > 0 or crustbox > 0 or toppingbox > 0: #Ensures that the size, crust type and topping of a pizza are all selected
            if sizebox==0 or crustbox == 0 or toppingbox == 0:
                QtGui.QMessageBox.information(self, "Error!", "You must choose the Size, Crust Type and Topping if you are ordering pizza.")
                oktogo=False   
        if oktogo==True:
                sql2 = """SELECT "ProductLineID" FROM "ProductLine" ORDER BY ProductLineID DESC LIMIT 1 """
                cur.execute(sql2)
                response = 0
                response = cur.fetchone()
                newproductid = response[0] + 1
                sql5 = """SELECT "OrderID" FROM "ProductLine" ORDER BY OrderID DESC LIMIT 1 """
                cur.execute(sql5)
                response = 0
                response = cur.fetchone()
                if secondorder == True:
                    neworderid = response[0]
                else:
                    neworderid = response[0] + 1
                    secondorder = True
                sql = """INSERT INTO "ProductLine" ("ProductLineID", "OrderID", "SizeID", "CrustID", "ToppingID", "ExtrasID", "DrinkID" ) VALUES ( ?, ?, ?, ?, ?, ?, ?)"""
                cur.execute(sql, (newproductid, neworderid, sizebox, crustbox, toppingbox, extrasbox, drinksbox, ))
                con.commit()
                self.hide()
                self.anotheragain = FourthWindow()
                self.anotheragain.show()

class FifthWindow(QtGui.QMainWindow, win5):     #This is the Order Confirmation window
    def __init__(self, parent=None):  #Constructor method
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)
        self.updatebutton.clicked.connect(self.update)
        self.returnhome.clicked.connect(self.home)
        self.printbutton.clicked.connect(self.printit)
        items  =[]
        overallpizza = 0
        drinkslist = 0
        extraslist = 0
        sql5 = """SELECT "OrderID" FROM "ProductLine" ORDER BY OrderID DESC LIMIT 1 """   #Retrieves the order that has just been saved
        cur.execute(sql5)
        orders = cur.fetchone()
        sql4 = """SELECT "SizeID", "CrustID", "ToppingID", "ExtrasID", "DrinkID" FROM ProductLine WHERE OrderID = '%d'""" % (orders[0])
        cur.execute(sql4)
        items = cur.fetchall()
        repeat = len(items)-1
        global ordernumber
        ordernumber = orders[0]
        sql9 = """SELECT "ProductLineID" FROM "ProductLine" WHERE "OrderID" = '%d'  """ %(ordernumber)
        cur.execute(sql9)
        con.commit()
        productlines = []
        productlines = cur.fetchall()
        timedate=time.strftime("%H:%M")+ " " + time.strftime("%d/%m/%Y")   #Takes the system time when saving the order into the 'Order' table
        for each in productlines:   #Adds each productline to the main orders table
            currenteach = each[0]
            sqladdproductline = """INSERT INTO "Orders" ("FullOrderID", "ProductLineID", "CustomerID", "TimeandDate", "StatusID") VALUES(?, ?, ?, ?, "1")"""
            cur.execute(sqladdproductline, (ordernumber, currenteach, usernameoptionsid[0][0], timedate))
            con.commit()
        drinks = []
        drinkprice = 0
        for eachdrink in items: #Selects the drinks ordered inorder to display them to the customer and calculate the cost
            sqldrinks = """SELECT "Drink" FROM Drinks WHERE DrinkID = '%d'""" % (eachdrink[4])
            cur.execute(sqldrinks)
            currentdrinks = cur.fetchone()
            drinks.append(currentdrinks)
        drinkslist = ""
        for each in drinks:
            try:
                drinkslist = drinkslist + " " + each[0]
                drinkprice = drinkprice + 2.99
            except:
                pass
            else:
                pass
        extras = []
        extrasprice = 0
        currentextra = []
        for eachextra in items:  #Selects the extras ordered inorder to display them to the customer and calculate the cost
            sqlextras = """SELECT "Extras" FROM Extras WHERE ExtrasID = '%d'""" % (eachextra[3])
            cur.execute(sqlextras)
            currentextra = cur.fetchone()
            extras.append(currentextra)
        extraslist = ""
        for each in extras:
            try:
                extraslist = extraslist + " " + each[0]
                extrasprice = extrasprice + 3.99
            except:
                pass
            else:
                pass
        pizzas = []
        pizzaprice = 0
        for eachpizza in items:   #Selects the pizzas ordered inorder to display them to the customer and calculate the cost
            sqlsize = """SELECT "Size" FROM Sizes WHERE SizeID = '%d'""" % (eachpizza[0])
            sqltopping = """SELECT "Topping" FROM Toppings WHERE ToppingID = '%d'""" % (eachpizza[2])
            sqlcrust = """SELECT "Crust" FROM StuffedCrust WHERE CrustID = '%d'""" % (eachpizza[1])
            cur.execute(sqlsize)
            currentsize = cur.fetchone()
            cur.execute(sqltopping)
            currenttopping = cur.fetchone()
            cur.execute(sqlcrust)
            currentcrust = cur.fetchone()
            pizzas.append(currentsize)
            pizzas.append(currenttopping)
            try: 
                if currentcrust[0] == "Yes":
                    newcrustlist = []
                    newcrustlist.append("Stuffed Crust")
                    pizzaprice=pizzaprice + 2.99
                    pizzaprice=pizzaprice + 7.99                    
            except:
                newcrustlist = []
            else:
                if currentcrust[0] == "No":
                    newcrustlist = []
                    newcrustlist.append("NOT Stuffed Crust")
                    pizzaprice=pizzaprice + 7.99
            pizzas.append(newcrustlist)
        pizzaslist = ""
        for each in pizzas:
            try:
                pizzaslist = pizzaslist + " " + each[0]
            except:
                pass
            else:
                pass
        sql = """SELECT "ProductLineID" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(ordernumber)
        cur.execute(sql)
        productlines = cur.fetchall()
        fullorder = []
        overallpizza = ""
        for eachline in productlines:
            sql2 = """SELECT "SizeID", "CrustID", "ToppingID", "ExtrasID", "DrinkID" FROM ProductLine WHERE ProductLineID = '%d'""" % (eachline[0])
            cur.execute(sql2)
            order=cur.fetchall()
            fullorder.append(order)
        extraslist= ""
        drinkslist=""
        for each in fullorder:
            size = each[0][0]
            sizesql = """SELECT "Size" FROM "Sizes" WHERE "SizeID" = '%d' """ %(size)
            cur.execute(sizesql)
            actualsize = cur.fetchone()
            crust = each[0][1]
            crustsql = """SELECT "Crust" FROM "StuffedCrust" WHERE "CrustID" = '%d' """ %(crust)
            cur.execute(crustsql)
            actualcrust = cur.fetchone()
            try:
                if actualcrust[0]=="Yes":
                    finalcrust = "Stuffed Crust"
                else:
                    finalcrust = "NOT Stuffed Crust"
            except:
                pass
            topping = each[0][2]
            toppingsql = """SELECT "Topping" FROM "Toppings" WHERE "ToppingID" = '%d' """ %(topping)
            cur.execute(toppingsql)
            actualtopping = cur.fetchone()
            try:
                overallpizza = overallpizza + actualsize[0] + " " + actualtopping[0] + " " + finalcrust + "                              " 
            except:
                pass
            else:
                pass
            extras = each[0][3]
            extrasql = """SELECT "Extras" FROM "Extras" WHERE "ExtrasID" = '%d' """ %(extras)
            cur.execute(extrasql)
            actualextras = cur.fetchone()
            try:
                extraslist = extraslist + actualextras[0] + "                                           "
            except:
                pass
            else:
                pass
            drinks = each[0][4]
            drinkssql = """SELECT "Drink" FROM "Drinks" WHERE "DrinkID" = '%d' """ %(drinks)
            cur.execute(drinkssql)
            actualdrinks = cur.fetchone()
            try:
                drinkslist = drinkslist + actualdrinks[0] + "                                           "
            except:
                pass
            else:
                pass
        self.pizzatable.setPlainText(overallpizza)    #Displays the ordered pizzas
        self.extrastable.setPlainText(extraslist)     #Displays the ordered extras
        self.drinkstable.setPlainText(drinkslist)     #Displays the ordered drinks
        cost = drinkprice + extrasprice + pizzaprice    
        cost2dp = "{0:.2f}".format(cost)        #Rounds cost of order, to 2 decimal places
        coststr = str(cost2dp)
        self.costbox.setPlainText(coststr)      #Displays the total cost
        sql = """UPDATE "Orders" SET "Cost"='%s' WHERE "FullOrderID"= '%s' """ %(coststr, ordernumber) #Saves cost of order
        cur.execute(sql)
        con.commit()
        sqlpayment = """SELECT "DeliveryType" FROM "CustomerInformation" WHERE "CustomerID" = '%d' """ %(usernameoptionsid[0])
        cur.execute(sqlpayment)
        method=cur.fetchone()
        methodstr=str(method[0])
        self.paymentmethodbox.setPlainText(methodstr)
        statussql = """SELECT "StatusID" FROM Orders WHERE "FullOrderID" = '%d' """ %(ordernumber)
        cur.execute(statussql)
        currentstatus = cur.fetchone()
        status = currentstatus[0]
        statusnamesql = """SELECT "Status" FROM Status WHERE "StatusID" = '%d' """ %(status)
        cur.execute(statusnamesql)
        currentstatusname = cur.fetchone()
        status = str(currentstatusname[0])        
        self.OrderStatus.setPlainText(status)
    def update(self):   #Function to refresh order status
        statussql = """SELECT "StatusID" FROM Orders WHERE "FullOrderID" = '%d' """ %(ordernumber)
        cur.execute(statussql)
        currentstatus = cur.fetchone()
        status = currentstatus[0]
        statusnamesql = """SELECT "Status" FROM Status WHERE "StatusID" = '%d' """ %(status)
        cur.execute(statusnamesql)
        currentstatusname = cur.fetchone()
        status = str(currentstatusname[0])        
        self.OrderStatus.setPlainText(status)
    def home(self): #Function to return to home menu
        self.hide()
        self.newwindow = TenthWindow()
        self.newwindow.show()
    def print1(self, printer = None):
            if(printer is None):
                printer = QtGui.QPrinter()
                if(QtGui.QPrintDialog(printer).exec_() != QtGui.QDialog.Accepted):
                    return
            self.label.print_(printer)
    def printit(self):  #This function is run if the user wishes to print the order confirmation 
        printer=QtGui.QPrinter()   #This calls the system print window
        dialog = QtGui.QPrintDialog(printer, self)
        if(dialog.exec_() != QtGui.QDialog.Accepted):
            return
        p=QtGui.QPixmap.grabWidget(self.frame)   #This specifies what is to be printed, in this case the frame called "frame"
        printLabel = QtGui.QLabel()
        printLabel.setPixmap(p)
        painter = QtGui.QPainter(printer)
        printLabel.render(painter)
        painter.end()        

class EighthWindow(QtGui.QMainWindow, win8): #This loads the GUI that is the staff's homescreen
    def __init__(self, parent=None):   #Setting up the window
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)
        self.selectbutton.clicked.connect(self.select)    #These connect the function to the appropiate button press
        self.chooseorder.returnPressed.connect(self.select)
        self.backbutton.clicked.connect(self.back)
        con.cursor()
        s=""" SELECT DISTINCT Orders.FullOrderID, Orders.TimeandDate, CustomerInformation.FirstName, CustomerInformation.Surname, Status.Status
        FROM Orders
        INNER JOIN Status
        ON Orders.StatusID=Status.StatusID
        INNER JOIN CustomerInformation
        ON Orders.CustomerID=CustomerInformation.CustomerID
        WHERE Orders.StatusID < 6
        """                    #This is one of my Inner Join queries, which joins together OrderID, order time, customer names and the order status
        cur.execute(s)
        self.data = cur.fetchall() #This fetches all the specified data, and then outputs it into a table
        if len(self.data)>0:
            for i in range(len(self.data)-1,-1):
                self.data.pop(i)
                self.model.removeRow(index.row(self.data[i]))
        self.model=QtGui.QStandardItemModel(self)     #This section of code creates the table seen in the GUI
        self.tableView.setModel(self.model)
        for row in self.data:    
                    items = [
                        QtGui.QStandardItem(str(field))
                        for field in row
                    ]
                    self.model.appendRow(items)
    def select(self): #This function is for selecting a specific order to load its details
        global chosenorder
        chosenorder = self.chooseorder.text()
        sql = """SELECT "ProductLineID" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(chosenorder)
        cur.execute(sql)
        productlines = cur.fetchall()
        if productlines==[]:
            pass
        else:
            self.hide()
            self.newwindow = NinthWindow() #Loads the order window
            self.newwindow.show()
    def back(self):
        self.hide()
        self.newwindow = SecondWindow()
        self.newwindow.show()

class NinthWindow(QtGui.QMainWindow, win9):   #This class controls the order view GUI for admin and staff
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)
        self.savebutton.clicked.connect(self.save)
        self.backbutton.clicked.connect(self.back)
        self.deleteorder.clicked.connect(self.delete)
        self.deleteorder.hide()
        self.label_3.setText("Staff Mode")
        backcheck = """SELECT "AccountType" FROM "CustomerInformation" WHERE "CustomerID" = '%d' """ %(usernameoptionsid[0])
        cur.execute(backcheck)
        ggj = cur.fetchone()
        if ggj[0]=="Admin":
            self.deleteorder.show()
            self.label_3.setText("Admin Mode") #The program checks which account type is logged in, and changes the label accordingly (Admin or staff)
        sql = """SELECT "ProductLineID" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(chosenorder)
        cur.execute(sql)
        productlines = cur.fetchall()
        fullorder = []
        overallpizza = ""
        for eachline in productlines: #Retrieves the requested order
            sql2 = """SELECT "SizeID", "CrustID", "ToppingID", "ExtrasID", "DrinkID" FROM ProductLine WHERE ProductLineID = '%d'""" % (eachline[0])
            cur.execute(sql2)
            order=cur.fetchall()
            fullorder.append(order)
        extraslist= ""
        drinkslist=""
        for each in fullorder:
            size = each[0][0]
            sizesql = """SELECT "Size" FROM "Sizes" WHERE "SizeID" = '%d' """ %(size)
            cur.execute(sizesql)
            actualsize = cur.fetchone()
            crust = each[0][1]
            crustsql = """SELECT "Crust" FROM "StuffedCrust" WHERE "CrustID" = '%d' """ %(crust)
            cur.execute(crustsql)
            actualcrust = cur.fetchone()
            try:
                if actualcrust[0]=="Yes":
                    finalcrust = "Stuffed Crust"
                else:
                    finalcrust = "NOT Stuffed Crust"
            except:
                pass
            topping = each[0][2]
            toppingsql = """SELECT "Topping" FROM "Toppings" WHERE "ToppingID" = '%d' """ %(topping)
            cur.execute(toppingsql)
            actualtopping = cur.fetchone()
            try:
                overallpizza = overallpizza + actualsize[0] + " " + finalcrust + " " + actualtopping[0] + "                              " 
            except:
                pass
            else:
                pass
            extras = each[0][3]
            extrasql = """SELECT "Extras" FROM "Extras" WHERE "ExtrasID" = '%d' """ %(extras)
            cur.execute(extrasql)
            actualextras = cur.fetchone()
            try:
                extraslist = extraslist + actualextras[0] + "                                           "
            except:
                pass
            else:
                pass
            drinks = each[0][4]
            drinkssql = """SELECT "Drink" FROM "Drinks" WHERE "DrinkID" = '%d' """ %(drinks)
            cur.execute(drinkssql)
            actualdrinks = cur.fetchone()
            try:
                drinkslist = drinkslist + actualdrinks[0] + "                                           "
            except:
                pass
            else:
                pass
        self.pizzatable.setPlainText(overallpizza) #Displays the order details
        self.extrastable.setPlainText(extraslist)
        self.drinkstable.setPlainText(drinkslist)
        global chosenorderint
        chosenorderint = int(chosenorder)
        sql7 = """SELECT "StatusID" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(chosenorderint)
        cur.execute(sql7)
        orderstatus = cur.fetchone()
        if orderstatus[0]==1:                   #This uses the current order status to activate the correct radio button
            self.radiowaiting.setChecked(True)
        if orderstatus[0]==2:
            self.radiopreparing.setChecked(True)            
        if orderstatus[0]==3:
            self.radiocooking.setChecked(True)
        if orderstatus[0]==4:
            self.radiodelivering.setChecked(True)
        if orderstatus[0]==5:
            self.radiofailed.setChecked(True)
        if orderstatus[0]==6:
            self.radiosuccessful.setChecked(True)            
    def save(self):  #Upon saving the order, the status is saved by setting the status to whatever radio button has been selected
        if self.radiowaiting.isChecked()==True:
            updatestatus = """UPDATE "Orders" SET "StatusID" = 1 WHERE "FullOrderID" = '%d' """ %(chosenorderint)
            cur.execute(updatestatus)
        if self.radiopreparing.isChecked()==True:
            updatestatus = """UPDATE "Orders" SET "StatusID" = 2 WHERE "FullOrderID" = '%d' """ %(chosenorderint)
            cur.execute(updatestatus)
        if self.radiocooking.isChecked()==True:
            updatestatus = """UPDATE "Orders" SET "StatusID" = 3 WHERE "FullOrderID" = '%d' """ %(chosenorderint)
            cur.execute(updatestatus)
        if self.radiodelivering.isChecked()==True:
            updatestatus = """UPDATE "Orders" SET "StatusID" = 4 WHERE "FullOrderID" = '%d' """ %(chosenorderint)
            cur.execute(updatestatus)
        if self.radiofailed.isChecked()==True:
            updatestatus = """UPDATE "Orders" SET "StatusID" = 5 WHERE "FullOrderID" = '%d' """ %(chosenorderint)
            cur.execute(updatestatus)
        if self.radiosuccessful.isChecked()==True:
            updatestatus = """UPDATE "Orders" SET "StatusID" = 6 WHERE "FullOrderID" = '%d' """ %(chosenorderint)
            cur.execute(updatestatus)
        con.commit() 
        backcheck = """SELECT "AccountType" FROM "CustomerInformation" WHERE "CustomerID" = '%d' """ %(usernameoptionsid[0])
        cur.execute(backcheck) #This is necessary to return the user to the correct previous screen, depending on whether they are admin or staff
        ggj = cur.fetchone()
        if ggj[0] == "Admin":
            self.hide()
            self.newwindow = FourteenthWindow()
            self.newwindow.show()
        if ggj[0] == "Staff":
            self.hide()
            self.newwindow = EighthWindow()
            self.newwindow.show()                              
    def back(self):
        backcheck = """SELECT "AccountType" FROM "CustomerInformation" WHERE "CustomerID" = '%d' """ %(usernameoptionsid[0])
        cur.execute(backcheck)
        ggj = cur.fetchone()
        if ggj[0] == "Admin":
            self.hide()
            self.newwindow = FourteenthWindow()
            self.newwindow.show()
        if ggj[0] == "Staff":
            self.hide()
            self.newwindow = EighthWindow()
            self.newwindow.show()                              
    def delete(self): #This deletes the order from the database
        sqldelete = """DELETE FROM Orders
            WHERE FullOrderID= '%s' """ %(chosenorder)
        cur.execute(sqldelete)
        sqldelete2 = """DELETE FROM ProductLine
            WHERE OrderID= '%s' """ %(chosenorder)  #The order is deleted from both the Orders and ProductLine tables, to maintain data integrity
        cur.execute(sqldelete2)
        con.commit()
        self.hide()
        self.newwindow = FourteenthWindow()
        self.newwindow.show()
        QtGui.QMessageBox.information(self, "Deleted", "Order deleted.")
        
class TenthWindow(QtGui.QMainWindow, win10): #This GUI is the homepage for the customer accounts
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)                          #Setting up UI / Button commands
        self.orderpizza.clicked.connect(self.order)
        self.backbutton.clicked.connect(self.back)
        self.personaldetails.clicked.connect(self.details)
        self.selectbutton.clicked.connect(self.select)
        self.chooseorder.returnPressed.connect(self.select)
        global usernameoptionsid
        sqlname = """SELECT "FirstName" FROM CustomerInformation WHERE CustomerID = '%d'""" % (usernameoptionsid[0])
        cur.execute(sqlname)
        firstnamereq = cur.fetchone()
        self.NameBox.setPlainText(firstnamereq[0])
        self.NameBox.setPlainText(firstnamereq[0])
        self.data=[]
        self.model = QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.model)
        self.load_data()                              
    def load_data(self):       
        cur = con.cursor()
        s=""" SELECT DISTINCT Orders.FullOrderID, Orders.TimeandDate, Orders.Cost, Status.Status
FROM Orders
INNER JOIN Status
ON Orders.StatusID=Status.StatusID
WHERE Orders.CustomerID = '%d'
        """ %(usernameoptionsid[0])   #This is another Inner Join query, bringing together relevant details from multiple tables
        cur.execute(s)
        self.data = cur.fetchall() #This creates the table in the GUI
        if len(self.data)>0:
            for i in range(len(self.data)-1,-1):
                self.data.pop(i)
                self.model.removeRow(index.row(self.data[i]))
        self.model=QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.model)
        for row in self.data:    
                    items = [
                        QtGui.QStandardItem(str(field))
                        for field in row
                    ]
                    self.model.appendRow(items)
    def select(self):
        global chosenorder
        chosenorder = self.chooseorder.text()
        sql = """SELECT "ProductLineID", "CustomerID" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(chosenorder)
        cur.execute(sql)
        productlines = cur.fetchall()
        if productlines==[]:
            pass
        elif productlines[0][1] != usernameoptionsid[0][0]:
            pass
        else:
            self.hide()
            self.newwindow = EleventhWindow()
            self.newwindow.show()
    def order(self):
        self.hide()
        self.newwindow = FourthWindow()
        self.newwindow.show()
    def back(self):
        self.hide()
        self.newwindow = SecondWindow()
        self.newwindow.show()
    def details(self):
        self.hide()
        self.newwindow = ThirteenthWindow()
        self.newwindow.show()

class EleventhWindow(QtGui.QMainWindow, win11):   #GUI for customer to see order
    def __init__(self, parent=None):              #Constructor Method
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)
        self.backbutton.clicked.connect(self.back)
        self.viewconfirmation.clicked.connect(self.view)
        sql = """SELECT "ProductLineID" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(chosenorder)   #Finds all productlines associated with the order
        cur.execute(sql)
        productlines = cur.fetchall()
        fullorder = []
        overallpizza = ""
        for eachline in productlines:   #Finds each item in each productline
            sql2 = """SELECT "SizeID", "CrustID", "ToppingID", "ExtrasID", "DrinkID" FROM ProductLine WHERE ProductLineID = '%d'""" % (eachline[0])
            cur.execute(sql2)
            order=cur.fetchall()
            fullorder.append(order)
        extraslist= ""
        drinkslist=""
        for each in fullorder:
            size = each[0][0]
            sizesql = """SELECT "Size" FROM "Sizes" WHERE "SizeID" = '%d' """ %(size)
            cur.execute(sizesql)
            actualsize = cur.fetchone()
            crust = each[0][1]
            crustsql = """SELECT "Crust" FROM "StuffedCrust" WHERE "CrustID" = '%d' """ %(crust)
            cur.execute(crustsql)
            actualcrust = cur.fetchone()
            try:
                if actualcrust[0]=="Yes":
                    finalcrust = "Stuffed Crust"
                else:
                    finalcrust = "NOT Stuffed Crust"
            except:
                pass
            topping = each[0][2]
            toppingsql = """SELECT "Topping" FROM "Toppings" WHERE "ToppingID" = '%d' """ %(topping)
            cur.execute(toppingsql)
            actualtopping = cur.fetchone()
            try:
                overallpizza = overallpizza + actualsize[0] + " " + actualtopping[0] + " " + finalcrust + "                              " 
            except:
                pass
            else:
                pass
            extras = each[0][3]
            extrasql = """SELECT "Extras" FROM "Extras" WHERE "ExtrasID" = '%d' """ %(extras)
            cur.execute(extrasql)
            actualextras = cur.fetchone()
            try:
                extraslist = extraslist + actualextras[0] + "                                           "
            except:
                pass
            else:
                pass
            drinks = each[0][4]
            drinkssql = """SELECT "Drink" FROM "Drinks" WHERE "DrinkID" = '%d' """ %(drinks)
            cur.execute(drinkssql)
            actualdrinks = cur.fetchone()
            try:
                drinkslist = drinkslist + actualdrinks[0] + "                                           "
            except:
                pass
            else:
                pass
        self.pizzatable.setPlainText(overallpizza)  #Outputs all pizza in the order
        self.extrastable.setPlainText(extraslist)   #Outputs all extras in the order
        self.drinkstable.setPlainText(drinkslist)   #Outputs all drinks in the order
        global chosenorderint
        chosenorderint = int(chosenorder)
        sql7 = """SELECT "StatusID" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(chosenorderint)
        cur.execute(sql7)
        orderstatus = cur.fetchone()    #Sets the correct radio button, depending on order status
        if orderstatus[0]==1:
            self.radiowaiting.setChecked(True)
        if orderstatus[0]==2:
            self.radiopreparing.setChecked(True)            
        if orderstatus[0]==3:
            self.radiocooking.setChecked(True)
        if orderstatus[0]==4:
            self.radiodelivering.setChecked(True)
        if orderstatus[0]==5:
            self.radiofailed.setChecked(True)
        if orderstatus[0]==6:
            self.radiosuccessful.setChecked(True)            
    def back(self):
        self.hide()
        self.newwindow = TenthWindow()
        self.newwindow.show()                             
    def view(self):    #Function to view order confirmation
        self.hide()
        self.newwindow = FifteenthPlusOneWindow()
        self.newwindow.show()

class TwelthWindow(QtGui.QMainWindow, win12):  #Account Creation Confirmation window
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)                           #Setup UI
        self.loginbutton.clicked.connect(self.login) #Controls Login button
    def login(self):    #Function runs when called by button press
        self.hide()        #Hides itself
        self.newwindow = SecondWindow()   #Opens login screen
        self.newwindow.show()

class ThirteenthWindow(QtGui.QMainWindow, win13):    #Window class to for customer to update details
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)                              #Setup UI
        self.submitbutton.clicked.connect(self.submit)   #Setup buttons
        self.cancelbutton.clicked.connect(self.cancel)
        sql = """SELECT "FirstName", "Surname", "HouseNumber", "Postcode", "MobileNumber", "DeliveryType", "UserName", "Password"  FROM CustomerInformation WHERE CustomerID = '%d'""" % (usernameoptionsid[0][0])
        cur.execute(sql)       #Selects all the details about the logged in user
        global currentdetails        #Makes the fetched details global so they can be accessed from other functions
        currentdetails = cur.fetchall()
        global mobilenumstr
        global housenumstr
        housenumstr = str(currentdetails[0][2])
        mobilenumstr = str(currentdetails[0][4])
        self.firstname.setPlainText(currentdetails[0][0])    #Set each textbox with the relevant info
        self.surname.setPlainText(currentdetails[0][1])
        self.housenum.setPlainText(housenumstr)
        self.postcode.setPlainText(currentdetails[0][3])
        self.mobilenum.setPlainText(mobilenumstr)
        self.payment.setPlainText(currentdetails[0][5])
        self.username.setPlainText(currentdetails[0][6])
        self.password.setPlainText("Password hidden")
    def cancel(self):   #Function to return to previous screen without saving
        self.hide()
        self.newwindow = TenthWindow()
        self.newwindow.show()                               
    def submit(self):   #Submit details
        newhousenum = self.housenumnew.text()    #Takes the input from the input boxes and stores them
        newpostcode = self.postcodenew.text()
        newmobilenum = self.mobilenumnew.text()
        newpayment = self.paymentmethodnew.currentText()
        newpassword = self.passwordnew.text()
        hashedpass = hasher(newpassword)
        if newhousenum == "":                    #This checks to see if any of the boxes are left blank,
            newhousenum = housenumstr            #and if they are, the new variables are set back to
        if newpostcode == "":                    #what they previously were
            newpostcode = currentdetails[0][3]   #so that empty values are not put in the database
        if newmobilenum == "":
            newmobilenum = mobilenumstr
        if newpayment == "":
            newpayment = currentdetails[0][5]
        if newpassword == "":
            newpassword = currentdetails[0][7]
        else:
            newpassword=hasher(newpassword)
        postcoderule = re.compile(r'^([A-PR-UWYZ0-9][A-HK-Y0-9][AEHMNPRTVXY0-9]?[ABEHMNPRVWXY0-9]? {1,2}[0-9][ABD-HJLN-UW-Z]{2}|GIR 0AA)$')
        if not postcoderule.search(newpostcode):     #REGEX validation on postcode
                QtGui.QMessageBox.information(self, "Error!", "Invalid Postcode \n Must be in format: 'XX12 3XX'")
        else:
            mobilerule = re.compile(r'^(07\d{9,9})$')     #REGEX validation on mobile number
            if not mobilerule.search(newmobilenum):
                QtGui.QMessageBox.information(self, "Error!", "Invalid Mobile Number \n Can only contain 11 numbers, starting with '07'")
            else:
                if len(newpassword) < 6:     #Validation on length of password
                    QtGui.QMessageBox.information(self, "Error!", "Password must contain at least 6 characters!")
                else:
                    sql = """UPDATE "CustomerInformation" SET HouseNumber='%s', Postcode='%s', MobileNumber ='%s', DeliveryType='%s', Password = '%s' WHERE "CustomerID" = '%s' """ %(newhousenum, newpostcode, newmobilenum, newpayment, newpassword, usernameoptionsid[0][0])
                    cur.execute(sql)    #Places the updated info back into the database
                    con.commit()
                    self.hide()
                    self.newwindow = TenthWindow()
                    self.newwindow.show()
        
class FourteenthWindow(QtGui.QMainWindow, win14):      #Admin home screen
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)                                  #Setting up UI
        self.editcustomerbutton.clicked.connect(self.edit)      #Setting up buttons
        self.selectbutton.clicked.connect(self.select)
        self.chooseorder.returnPressed.connect(self.select)    #Making pressing return act the same as pressing the button
        self.databutton.clicked.connect(self.data)
        self.backbutton.clicked.connect(self.back)
        self.data=[]
        self.model = QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.model)
        self.load_data()                                
    def load_data(self):        #Creates a table in the GUI for the admin
        cur = con.cursor()
        s="""SELECT DISTINCT Orders.FullOrderID, Orders.TimeandDate, CustomerInformation.FirstName, CustomerInformation.Surname, Status.Status
        FROM Orders
        INNER JOIN Status
        ON Orders.StatusID=Status.StatusID
        INNER JOIN CustomerInformation
        ON Orders.CustomerID=CustomerInformation.CustomerID
	"""
        cur.execute(s)       #Selects the details of all orders in database using an inner join query
        self.data = cur.fetchall() 
        if len(self.data)>0:         #Creates the table
            for i in range(len(self.data)-1,-1):
                self.data.pop(i)
                self.model.removeRow(index.row(self.data[i]))
        self.model=QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.model)
        for row in self.data:    
                    items = [
                        QtGui.QStandardItem(str(field))
                        for field in row
                    ]
                    self.model.appendRow(items)                                 
    def select(self):    #Selecting a specific order
        global chosenorder
        chosenorder = self.chooseorder.text()
        sql = """SELECT "ProductLineID" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(chosenorder)   #Querying database for specific order
        cur.execute(sql)
        productlines = cur.fetchall()
        if productlines==[]:    #Does nothing if the order cannot be found
            pass
        else:
            self.hide()
            self.newwindow = NinthWindow()   #otherwise, it opens the order view window
            self.newwindow.show()
    def back(self):   #FUnction to go back to login screen
        self.hide()
        self.newwindow = SecondWindow()
        self.newwindow.show()
    def edit(self):      #View all customer details
        self.hide()
        self.newwindow = FifteenthWindow()
        self.newwindow.show()
    def data(self):      #View data analytics
        self.hide()
        self.newwindow = SeventeenthWindow()
        self.newwindow.show()

class FifteenthWindow(QtGui.QMainWindow, win15):  #GUI to view all user details
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)                      #Setup UI
        self.backbutton.clicked.connect(self.back)
        self.deletebutton.clicked.connect(self.delete)
        self.data=[]
        self.model = QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.model)
        self.load_data()
        self.selectbutton.clicked.connect(self.upd_record)
    def upd_record(self):
        index = self.tableView.currentIndex() #returns currently selected cell
        cell_contents=index.data()#returns the contents of the currently selected cell
        idcust=self.model.data(self.model.index(index.row(), 0))
        firstname=self.model.data(self.model.index(index.row(), 1))
        surname=self.model.data(self.model.index(index.row(), 2))
        house=self.model.data(self.model.index(index.row(), 3))
        postcode=self.model.data(self.model.index(index.row(), 4))
        mobile=self.model.data(self.model.index(index.row(), 5))
        pay=self.model.data(self.model.index(index.row(), 6))
        user=self.model.data(self.model.index(index.row(), 7))
        password=self.model.data(self.model.index(index.row(), 8))
        hashedpass = hasher(password)
        typeaccount=self.model.data(self.model.index(index.row(), 9))
        statusaccount=self.model.data(self.model.index(index.row(), 10))
        question=self.model.data(self.model.index(index.row(), 11))
        answer=self.model.data(self.model.index(index.row(), 12))
        self.model.data(self.model.index(4,1))
        s='UPDATE CustomerInformation SET FirstName=?,Surname=?,HouseNumber=?,Postcode=?,MobileNumber=?,DeliveryType=?, Password=?, AccountType=?, AccountStatus=?, SecurityQuestion=?, SecurityAnswer=? WHERE CustomerID=?'
        cur.execute(s,(firstname,surname,house, postcode, mobile, pay, hashedpass, typeaccount, statusaccount, question, answer, idcust))
        con.commit()
        self.load_data()                                
    def load_data(self):    #Loads the info and creates a table
        cur = con.cursor()
        s='select * from CustomerInformation' #Selects entire table
        cur.execute(s)
        self.data = cur.fetchall() 
        if len(self.data)>0:         #Creates table in GUI
            for i in range(len(self.data)-1,-1):
                self.data.pop(i)
                self.model.removeRow(index.row(self.data[i]))
        self.model=QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.model)
        for row in self.data:    
                    items = [
                        QtGui.QStandardItem(str(field))
                        for field in row
                    ]
                    self.model.appendRow(items)                                 
    def back(self):      #Back function
        self.hide()
        self.newwindow = FourteenthWindow()
        self.newwindow.show()
    def delete(self):    #Suspend users function
        index = self.tableView.currentIndex()
        typeaccount=self.model.data(self.model.index(index.row(), 9))   #Works out customer ID of selected account
        if typeaccount == "Admin":
            QtGui.QMessageBox.information(self, "Error!", "Cannot suspend Admin or Staff accounts!")  #Stops admin suspending admin/staff accounts
        elif typeaccount == "Staff":
            QtGui.QMessageBox.information(self, "Error!", "Cannot suspend Admin or Staff accounts!")    
        else:
            typeactive=self.model.data(self.model.index(index.row(), 10)) #Determines whether account is active or already suspended
            if typeactive == "Active":
                idcust=self.model.data(self.model.index(index.row(), 0))
                sqlupdate="""UPDATE CustomerInformation SET AccountStatus="Suspended" WHERE CustomerID= '%s'""" %(idcust)  #Update database
                cur.execute(sqlupdate)
                con.commit()
                self.load_data()
                QtGui.QMessageBox.information(self, "Suspended", "Account Suspended.")
            else:
                idcust=self.model.data(self.model.index(index.row(), 0))
                sqlupdate="""UPDATE CustomerInformation SET AccountStatus="Active" WHERE CustomerID= '%s'""" %(idcust) #Update database
                cur.execute(sqlupdate)
                con.commit()
                self.load_data()
                QtGui.QMessageBox.information(self, "Reactivated", "Account Re-activated.")
            
class FifteenthPlusOneWindow(QtGui.QMainWindow, win5):  #previous order GUI
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)    #Setup UI 
        self.returnhome.clicked.connect(self.back)
        self.printbutton.clicked.connect(self.printit)
        self.updatebutton.clicked.connect(self.update)
        sql = """SELECT "ProductLineID" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(chosenorder)  #Finds all productlines in order
        cur.execute(sql)
        productlines = cur.fetchall()
        fullorder = []
        overallpizza = ""
        for eachline in productlines:  #Finds items in each productline
            sql2 = """SELECT "SizeID", "CrustID", "ToppingID", "ExtrasID", "DrinkID" FROM ProductLine WHERE ProductLineID = '%d'""" % (eachline[0])
            cur.execute(sql2)
            order=cur.fetchall()
            fullorder.append(order)
        extraslist= ""
        drinkslist=""
        for each in fullorder:
            size = each[0][0]
            sizesql = """SELECT "Size" FROM "Sizes" WHERE "SizeID" = '%d' """ %(size)
            cur.execute(sizesql)
            actualsize = cur.fetchone()
            crust = each[0][1]
            crustsql = """SELECT "Crust" FROM "StuffedCrust" WHERE "CrustID" = '%d' """ %(crust)
            cur.execute(crustsql)
            actualcrust = cur.fetchone()
            try:
                if actualcrust[0]=="Yes":
                    finalcrust = "Stuffed Crust"
                else:
                    finalcrust = "NOT Stuffed Crust"
            except:
                pass
            topping = each[0][2]
            toppingsql = """SELECT "Topping" FROM "Toppings" WHERE "ToppingID" = '%d' """ %(topping)
            cur.execute(toppingsql)
            actualtopping = cur.fetchone()
            try:
                overallpizza = overallpizza + actualsize[0] + " " + actualtopping[0] + " " + finalcrust + "                              " 
            except:
                pass
            else:
                pass
            extras = each[0][3]
            extrasql = """SELECT "Extras" FROM "Extras" WHERE "ExtrasID" = '%d' """ %(extras)
            cur.execute(extrasql)
            actualextras = cur.fetchone()
            try:
                extraslist = extraslist + actualextras[0] + "                                           "
            except:
                pass
            else:
                pass
            drinks = each[0][4]
            drinkssql = """SELECT "Drink" FROM "Drinks" WHERE "DrinkID" = '%d' """ %(drinks)
            cur.execute(drinkssql)
            actualdrinks = cur.fetchone()
            try:
                drinkslist = drinkslist + actualdrinks[0] + "                                           "
            except:
                pass
            else:
                pass
        self.pizzatable.setPlainText(overallpizza)   #Outputs pizzas ordered
        self.extrastable.setPlainText(extraslist)    #Outputs extras ordered
        self.drinkstable.setPlainText(drinkslist)    #Outputs drinks ordered
        sqlcost = """SELECT "Cost" FROM "Orders" WHERE "FullOrderID" = '%s' """ %(chosenorder)
        cur.execute(sqlcost)
        method1=cur.fetchone()
        self.costbox.setPlainText(method1[0])  #Finds and outputs cost stored in database
        sqlpayment = """SELECT "DeliveryType" FROM "CustomerInformation" WHERE "CustomerID" = '%d' """ %(usernameoptionsid[0])
        cur.execute(sqlpayment)
        method=cur.fetchone()
        methodstr=str(method[0])
        self.paymentmethodbox.setPlainText(methodstr)    #Finds and outputs payment method stored in database
        statussql = """SELECT "StatusID" FROM Orders WHERE "FullOrderID" = '%s' """ %(chosenorder)
        cur.execute(statussql)
        currentstatus = cur.fetchone()
        status = currentstatus[0]   
        statusnamesql = """SELECT "Status" FROM Status WHERE "StatusID" = '%d' """ %(status)
        cur.execute(statusnamesql)
        currentstatusname = cur.fetchone()
        status = str(currentstatusname[0])        
        self.OrderStatus.setPlainText(status)  #Finds and outputs order status in database
    def back(self):   #Go back function
        self.hide()
        self.newwindow = TenthWindow()
        self.newwindow.show()                               
    def print1(self, printer = None):
            if(printer is None):
                printer = QtGui.QPrinter()
                if(QtGui.QPrintDialog(printer).exec_() != QtGui.QDialog.Accepted):
                    return
            self.label.print_(printer)                               
    def printit(self):     #Print function
        printer=QtGui.QPrinter()
        dialog = QtGui.QPrintDialog(printer, self)
        if(dialog.exec_() != QtGui.QDialog.Accepted):
            return
        p=QtGui.QPixmap.grabWidget(self.frame)  #Prints the specified frame
        printLabel = QtGui.QLabel()
        printLabel.setPixmap(p)
        painter = QtGui.QPainter(printer)
        printLabel.render(painter)
        painter.end()                               
    def update(self):     #Updates the order status
        statussql = """SELECT "StatusID" FROM Orders WHERE "FullOrderID" = '%d' """ %(chosenorderint)
        cur.execute(statussql)
        currentstatus = cur.fetchone()
        status = currentstatus[0]
        statusnamesql = """SELECT "Status" FROM Status WHERE "StatusID" = '%d' """ %(status)
        cur.execute(statusnamesql)
        currentstatusname = cur.fetchone()
        status = str(currentstatusname[0])        
        self.OrderStatus.setPlainText(status)

class SixteenthWindow(QtGui.QMainWindow, win16):   #Password recovery GUI
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)
        self.back.clicked.connect(self.cancel)
        self.search.clicked.connect(self.searchpressed)
        self.usernamebox.returnPressed.connect(self.searchpressed)
        self.answerbox.returnPressed.connect(self.submitpressed)
        self.newpassword.returnPressed.connect(self.changepressed)
        self.submit.clicked.connect(self.submitpressed)
        self.change.clicked.connect(self.changepressed)
        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(2, False)
    def searchpressed(self):    #Search for username function
        search = self.usernamebox.text()
        searchsql = """SELECT * FROM CustomerInformation WHERE UserName = '%s' """ %(search)   #Searches Customer table for username
        cur.execute(searchsql)
        global details
        details = cur.fetchall()
        if details==[]:    #If no account found
            QtGui.QMessageBox.information(self, "Account Not Found", "This username is not stored in the system. \n Please try again...")
            self.hide()
            self.reload= SixteenthWindow()
            self.reload.show()
        else:
            if details[0][10] == "Suspended":    #If account suspended, denies entry
                QtGui.QMessageBox.information(self, "Account Suspended", "This account has been suspended. \n Contact the system administrator.")
                self.hide()
                self.reload= SixteenthWindow()
                self.reload.show()
            elif details[0][9] == "Admin" or details[0][9] == "Staff":   #Can only be used by customer accounts, not admin/staff
                QtGui.QMessageBox.information(self, "Error!", "The password recovery tool is for Customer accounts only. \n Contact the system administrator.")
                self.hide()
                self.reload= SixteenthWindow()
                self.reload.show()
            else:
                self.tabWidget.setTabEnabled(1, True)  #If account found, enables next tab and disables current one
                QtGui.QMessageBox.information(self, "Account Found", "Answer the security question on the next tab to access your account.")
                self.tabWidget.setCurrentIndex(1)
                self.tabWidget.setTabEnabled(0, False)
                self.questionbox.setPlainText(details[0][11])   #Outputs security question
    def submitpressed(self):   #Function to check security question
        answer=self.answerbox.text()
        if answer == details[0][12]:   #Compares inputted answer to actual answer
            self.tabWidget.setTabEnabled(2, True)    #If correct, eanbles the next tab
            QtGui.QMessageBox.information(self, "Success", "You have correctly answered the security question. \n Reset your password on the next screen...")
            self.tabWidget.setCurrentIndex(2)
            self.tabWidget.setTabEnabled(1, False)    #And disables the current tab
        else:
            QtGui.QMessageBox.information(self, "Incorrect Details", "You have incorrectly answered the security question. \n Try again...") 
    def changepressed(self):                    #Function to change password
        passwordnew = self.newpassword.text()
        if passwordnew == "":
            QtGui.QMessageBox.information(self, "Error!", "You need to enter a password...")
        elif len(passwordnew) < 6:   #Password validation
            QtGui.QMessageBox.information(self, "Error!", "Password must contain at least 6 characters!")
        else:
            hashedpass=hasher(passwordnew)
            print(hashedpass)
            updatepassword = """UPDATE CustomerInformation SET Password='%s' WHERE CustomerID = '%s' """ %(hashedpass, details[0][0])
            cur.execute(updatepassword)  #Saves password to database
            con.commit()
            QtGui.QMessageBox.information(self, "Password Changed", "Your password has been changed.")
            self.hide()
            self.newwindow=SecondWindow()   #Returns to login window
            self.newwindow.show()
    def cancel(self):   #Cancels password recovery
        self.hide()
        self.newwindow = SecondWindow()
        self.newwindow.show()

class SeventeenthWindow(QtGui.QMainWindow, win17):        #Data Analytics window
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)                                #Setup UI
        self.backbutton.clicked.connect(self.back)
        sqlorders=  """SELECT COUNT( DISTINCT FullOrderID) FROM Orders"""    #Counts total orders
        cur.execute(sqlorders)
        ordertotal=cur.fetchone()
        self.totalorders.setPlainText(str(ordertotal[0]))
        cur.execute("SELECT DISTINCT FullOrderID FROM Orders")
        distinctorders= cur.fetchall()
        revtotal=0
        for each in distinctorders:   #Adds up cost of each order
            sqlrev=  """SELECT Cost FROM Orders WHERE FullOrderID='%s'""" %(each[0])
            cur.execute(sqlrev)
            rev=cur.fetchone()
            revtotal=revtotal+float(rev[0])
        revtotal="{0:.2f}".format(revtotal)      #Rounds total cost to 2 decimal places
        self.totalrev.setPlainText("£ "+str(revtotal))
        sqlaccounts=  """SELECT COUNT(CustomerID) FROM CustomerInformation  WHERE AccountType= 'Customer'"""   #Counts the customer accounts
        cur.execute(sqlaccounts)
        acctotal=cur.fetchone()
        self.totalaccounts.setPlainText(str(acctotal[0]))
        avgcost=float(revtotal)/ordertotal[0]    #Works out average cost of order
        avgcost="{0:.2f}".format(avgcost)        #Rounds average cost to 2 dp
        self.avgrev.setPlainText("£ "+str(avgcost))
        sqlactive="""SELECT COUNT(DISTINCT CustomerID) FROM Orders"""
        cur.execute(sqlactive)
        activeacc=cur.fetchone()
        self.activeaccounts.setPlainText(str(activeacc[0]))    #Outputs number of active accounts
        sqltoppings="""SELECT ToppingID FROM ProductLine"""     #Fetches all toppings ever ordered
        cur.execute(sqltoppings)
        toppingdata=cur.fetchall()
        margcount=0
        peppcount=0
        chickcount=0
        meatcount=0
        vegcount=0
        hawcount=0
        for each in toppingdata:     #Tallies up each type of topping
            if each[0]==1:
                margcount=margcount+1
            if each[0]==2:
                peppcount=peppcount+1
            if each[0]==3:
                chickcount=chickcount+1
            if each[0]==4:
                meatcount=meatcount+1
            if each[0]==5:
               vegcount=vegcount+1
            if each[0]==6:
                hawcount=hawcount+1
                #All HTML charts from amcharts:
        toppings="""
<!DOCTYPE html>
<html>
	<head>
		
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/amcharts.js"></script>
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/pie.js"></script>
		

		<script type="text/javascript">
			AmCharts.makeChart("chartdiv",
				{
					"type": "pie",
					"angle": 11.7,
					"balloonText": "[[title]]<br><span style='font-size:14px'><b>[[value]]</b> ([[percents]]%)</span>",
					"depth3D": 15,
					"innerRadius": 20,
					"labelRadius": 10,
					"minRadius": 0,
					"marginBottom": 0,
					"marginTop": 0,
					"outlineThickness": 2,
					"pullOutOnlyOne": true,
					"startDuration": 4,
					"startEffect": "elastic",
					"titleField": "category",
					"valueField": "column-1",
					"theme": "default",
					"allLabels": [],
					"balloon": {
						"animationDuration": 0,
						"borderThickness": 1,
						"fadeOutDuration": 0,
						"fontSize": 0,
						"maxWidth": 0,
						"pointerWidth": 0
					},
					"legend": {
						"enabled": false,
						"accessibleLabel": "",
						"align": "center",
						"labelText": "",
						"markerType": "circle",
						"rollOverGraphAlpha": 0
					},
					"titles": [],
					"dataProvider": [
						{
							"category": "Margherita",
							"column-1": z1
						},
						{
							"category": "Pepperoni",
							"column-1": z2
						},
						{
							"category": "Chicken",
							"column-1": z3
						},
						{
							"category": "Meat Feast",
							"column-1": z4
						},
						{
							"category": "Vegetable",
							"column-1": z5
						},
						{
							"category": "Hawaiian",
							"column-1": z6
						}
					]
				}
			);
		</script>
	</head>
	<body>
		<div id="chartdiv" style="width: 100%; height: 400px; background-color: #FFFFFF;" ></div>
	</body>
</html>
"""
        toppings=toppings.replace("z1",str(margcount))    #Replaces 'z1' (etc) in the HTML string above with actual value
        toppings=toppings.replace("z2",str(peppcount))
        toppings=toppings.replace("z3",str(chickcount))
        toppings=toppings.replace("z4",str(meatcount))
        toppings=toppings.replace("z5",str(vegcount))
        toppings=toppings.replace("z6",str(hawcount))
        self.webViewtopping.setHtml(toppings)    #Sets the webview in the GUI to display the HTML pie chart in the string above
        sqldrinks="""SELECT DrinkID FROM ProductLine"""    #Fetches all drinks ever ordered
        cur.execute(sqldrinks)
        drinkdata=cur.fetchall()
        colacount=0
        lemoncount=0
        pepsicount=0
        fantacount=0
        for each in drinkdata:    #Tallies up each type of drink
            if each[0]==1:
                colacount=colacount+1
            if each[0]==2:
                lemoncount=lemoncount+1
            if each[0]==3:
                pepsicount=pepsicount+1
            if each[0]==4:
                fantacount=fantacount+1
        drinks="""
<!DOCTYPE html>
<html>
	<head>
		
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/amcharts.js"></script>
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/pie.js"></script>
		

		<script type="text/javascript">
			AmCharts.makeChart("chartdiv",
				{
					"type": "pie",
					"angle": 11.7,
					"balloonText": "[[title]]<br><span style='font-size:14px'><b>[[value]]</b> ([[percents]]%)</span>",
					"depth3D": 15,
					"innerRadius": 20,
					"labelRadius": 10,
					"minRadius": 0,
					"marginBottom": 0,
					"marginTop": 0,
					"outlineThickness": 2,
					"pullOutOnlyOne": true,
					"startDuration": 4,
					"startEffect": "elastic",
					"titleField": "category",
					"valueField": "column-1",
					"theme": "default",
					"allLabels": [],
					"balloon": {
						"animationDuration": 0,
						"borderThickness": 1,
						"fadeOutDuration": 0,
						"fontSize": 0,
						"maxWidth": 0,
						"pointerWidth": 0
					},
					"legend": {
						"enabled": false,
						"accessibleLabel": "",
						"align": "center",
						"labelText": "",
						"markerType": "circle",
						"rollOverGraphAlpha": 0
					},
					"titles": [],
					"dataProvider": [
						{
							"category": "Coca Cola",
							"column-1": z1
						},
						{
							"category": "Lemonade",
							"column-1": z2
						},
						{
							"category": "Pepsi",
							"column-1": z3
						},
						{
							"category": "Fanta",
							"column-1": z4
						},
						
					]
				}
			);
		</script>
	</head>
	<body>
		<div id="chartdiv" style="width: 100%; height: 400px; background-color: #FFFFFF;" ></div>
	</body>
</html>
"""
        drinks=drinks.replace("z1",str(colacount))      #Replaces 'z1' (etc) in the HTML string above with actual value
        drinks=drinks.replace("z2",str(lemoncount))
        drinks=drinks.replace("z3",str(pepsicount))
        drinks=drinks.replace("z4",str(fantacount))
        self.webViewdrink.setHtml(drinks)     #Sets the webview in the GUI to display the HTML pie chart in the string above
        sqlsize="""SELECT SizeID FROM ProductLine"""    #Fetches all pizza sizes ever ordered
        cur.execute(sqlsize)
        sizedata=cur.fetchall()
        ninecount=0
        twelvecount=0
        fifteencount=0
        eighteencount=0
        for each in sizedata:    #Tallies up each type of pizza size
            if each[0]==1:
                ninecount=ninecount+1
            if each[0]==2:
                twelvecount=twelvecount+1
            if each[0]==3:
                fifteencount=fifteencount+1
            if each[0]==4:
                eighteencount=eighteencount+1
        sizes="""
<!DOCTYPE html>
<html>
	<head>
		
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/amcharts.js"></script>
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/pie.js"></script>
		

		<script type="text/javascript">
			AmCharts.makeChart("chartdiv",
				{
					"type": "pie",
					"angle": 11.7,
					"balloonText": "[[title]]<br><span style='font-size:14px'><b>[[value]]</b> ([[percents]]%)</span>",
					"depth3D": 15,
					"innerRadius": 20,
					"labelRadius": 10,
					"minRadius": 0,
					"marginBottom": 0,
					"marginTop": 0,
					"outlineThickness": 2,
					"pullOutOnlyOne": true,
					"startDuration": 4,
					"startEffect": "elastic",
					"titleField": "category",
					"valueField": "column-1",
					"theme": "default",
					"allLabels": [],
					"balloon": {
						"animationDuration": 0,
						"borderThickness": 1,
						"fadeOutDuration": 0,
						"fontSize": 0,
						"maxWidth": 0,
						"pointerWidth": 0
					},
					"legend": {
						"enabled": false,
						"accessibleLabel": "",
						"align": "center",
						"labelText": "",
						"markerType": "circle",
						"rollOverGraphAlpha": 0
					},
					"titles": [],
					"dataProvider": [
						{
							"category": "9 Inches",
							"column-1": z1
						},
						{
							"category": "12 Inches",
							"column-1": z2
						},
						{
							"category": "15 Inches",
							"column-1": z3
						},
						{
							"category": "18 Inches",
							"column-1": z4
						},
						
					]
				}
			);
		</script>
	</head>
	<body>
		<div id="chartdiv" style="width: 100%; height: 400px; background-color: #FFFFFF;" ></div>
	</body>
</html>
"""
        sizes=sizes.replace("z1",str(ninecount))        #Replaces 'z1' (etc) in the HTML string above with actual value
        sizes=sizes.replace("z2",str(twelvecount))
        sizes=sizes.replace("z3",str(fifteencount))
        sizes=sizes.replace("z4",str(eighteencount))
        self.webViewsize.setHtml(sizes)     #Sets the webview in the GUI to display the HTML pie chart in the string above
        sqlcrust="""SELECT CrustID FROM ProductLine"""    #Fetches all crusts ever ordered
        cur.execute(sqlcrust)
        crustdata=cur.fetchall()
        yescount=0
        nocount=0
        for each in crustdata:    #Tallies up each type of crust
            if each[0]==1:
                yescount=yescount+1
            if each[0]==2:
                nocount=nocount+1
        crusts="""
<!DOCTYPE html>
<html>
	<head>
		
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/amcharts.js"></script>
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/pie.js"></script>
		

		<script type="text/javascript">
			AmCharts.makeChart("chartdiv",
				{
					"type": "pie",
					"angle": 11.7,
					"balloonText": "[[title]]<br><span style='font-size:14px'><b>[[value]]</b> ([[percents]]%)</span>",
					"depth3D": 15,
					"innerRadius": 20,
					"labelRadius": 10,
					"minRadius": 0,
					"marginBottom": 0,
					"marginTop": 0,
					"outlineThickness": 2,
					"pullOutOnlyOne": true,
					"startDuration": 4,
					"startEffect": "elastic",
					"titleField": "category",
					"valueField": "column-1",
					"theme": "default",
					"allLabels": [],
					"balloon": {
						"animationDuration": 0,
						"borderThickness": 1,
						"fadeOutDuration": 0,
						"fontSize": 0,
						"maxWidth": 0,
						"pointerWidth": 0
					},
					"legend": {
						"enabled": false,
						"accessibleLabel": "",
						"align": "center",
						"labelText": "",
						"markerType": "circle",
						"rollOverGraphAlpha": 0
					},
					"titles": [],
					"dataProvider": [
						{
							"category": "Stuffed",
							"column-1": z1
						},
						{
							"category": "Regular",
							"column-1": z2
						},
						
						
					]
				}
			);
		</script>
	</head>
	<body>
		<div id="chartdiv" style="width: 100%; height: 400px; background-color: #FFFFFF;" ></div>
	</body>
</html>
"""
        crusts=crusts.replace("z1",str(yescount))    #Replaces 'z1' (etc) in the HTML string above with actual value
        crusts=crusts.replace("z2",str(nocount))
        self.webViewcrust.setHtml(crusts)     #Sets the webview in the GUI to display the HTML pie chart in the string above
        sqlextra="""SELECT ExtrasID FROM ProductLine"""    #Fetches all extras ever ordered
        cur.execute(sqlextra)
        extrasdata=cur.fetchall()
        garliccount=0
        wedgescount=0
        for each in extrasdata:    #Tallies up each type of extra
            if each[0]==1:
                garliccount=garliccount+1
            if each[0]==2:
                wedgescount=wedgescount+1
        extras="""
<!DOCTYPE html>
<html>
	<head>
		
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/amcharts.js"></script>
		<script type="text/javascript" src="https://www.amcharts.com/lib/3/pie.js"></script>
		

		<script type="text/javascript">
			AmCharts.makeChart("chartdiv",
				{
					"type": "pie",
					"angle": 11.7,
					"balloonText": "[[title]]<br><span style='font-size:14px'><b>[[value]]</b> ([[percents]]%)</span>",
					"depth3D": 15,
					"innerRadius": 20,
					"labelRadius": 10,
					"minRadius": 0,
					"marginBottom": 0,
					"marginTop": 0,
					"outlineThickness": 2,
					"pullOutOnlyOne": true,
					"startDuration": 4,
					"startEffect": "elastic",
					"titleField": "category",
					"valueField": "column-1",
					"theme": "default",
					"allLabels": [],
					"balloon": {
						"animationDuration": 0,
						"borderThickness": 1,
						"fadeOutDuration": 0,
						"fontSize": 0,
						"maxWidth": 0,
						"pointerWidth": 0
					},
					"legend": {
						"enabled": false,
						"accessibleLabel": "",
						"align": "center",
						"labelText": "",
						"markerType": "circle",
						"rollOverGraphAlpha": 0
					},
					"titles": [],
					"dataProvider": [
						{
							"category": "Garlic <br> bread",
							"column-1": z1
						},
						{
							"category": "Potato <br> Wedges",
							"column-1": z2
						},
						
						
					]
				}
			);
		</script>
	</head>
	<body>
		<div id="chartdiv" style="width: 100%; height: 400px; background-color: #FFFFFF;" ></div>
	</body>
</html>
"""
        extras=extras.replace("z1",str(garliccount))     #Replaces 'z1' (etc) in the HTML string above with actual value
        extras=extras.replace("z2",str(wedgescount))
        self.webViewextra.setHtml(extras)      #Sets the webview in the GUI to display the HTML pie chart in the string above                             
    def back(self):    #Back function
        self.hide()
        self.newwindow=FourteenthWindow()
        self.newwindow.show()
    
class EighteenthWindow(QtGui.QMainWindow, win18):   #Postcode Checker GUI
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)        
        self.setupUi(self)    #Setup UI
        self.okbutton.clicked.connect(self.ok)
        global verifiedpostcode
        verifiedpostcode=True
        gmaps="""
<!doctype html>
<html>
   <head>
      <style type="text/css">
        #map
        {
          height:285px;
          width:100;
          display:block;
        }
      </style>

     
      <script src="http://maps.googleapis.com/maps/api/js?key=AIzaSyDRok8mK95-H3pDP2jvOB4DF9XtXLsCP2s&sensor=false&libraries=geometry" type="text/javascript"></script>
                                    <script>
                                        var geocoder;
                                        var map;
                                       

                                        function initialize() {
                                          geocoder = new google.maps.Geocoder();
                                          var latlng = new google.maps.LatLng(51.6409256,-0.73800);
                                          var mapOptions = {
                                            zoom: 11,
                                            center: latlng,
                                            disableDefaultUI: true,
                                            zoomControl: true,
                                            mapTypeControl: false,
                                            scaleControl: true,
                                            streetViewControl: false,
                                            rotateControl: false,
                                            fullscreenControl: false,
                                            mapTypeId: google.maps.MapTypeId.ROADMAP
                                          }
                                          
                                          map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
                                          var shoplocation = new google.maps.LatLng(51.6409256,-0.73800);
                                          var shopmarker = new google.maps.Marker({position:shoplocation});
                                          
                                          shopmarker.setMap(map);
                                          var radius = new google.maps.Circle({
                                          center: shoplocation,
                                          radius: 10000,
                                          strokeColor: "#0000FF",
                                          strokeOpacity: 0.4,
                                          strokeWeight: 1,
                                          fillColor: "#0000FF",
                                          fillOpacity: 0.05
                                          });
                                          radius.setMap(map);

                                          codeAddress();
                                          
                                        }
                                        

                                        function codeAddress() {
                                          var address = 'z1';
                                          geocoder.geocode( { 'address': address}, function(results, status) {
                                            if (status == google.maps.GeocoderStatus.OK) {
                                              map.setCenter(results[0].geometry.location);
                                              var newmarker = results[0].geometry.location;


                                              var marker = new google.maps.Marker({
                                                map: map,
                                                position: results[0].geometry.location
                                              });
                                              var shopcoord = new google.maps.LatLng(51.6409256,-0.73800);

                                              var p2 = new google.maps.LatLng(51.6409256,-0.73800);




                                              //traveldi=calcDistance(shopcoord, newmarker);
                                              //alert(traveldi)
                                              

                                              
                                          }})
                                        }
                                        
                                        //calculates distance between two points in km's
                                        function calcDistance(shopcoord, newmarker) {
                                          //alert(shopcoord)
                                          //alert(newmarker)
                                          //alert("HH")
                                          //alert(calcDistance)
                                          return (google.maps.geometry.spherical.computeDistanceBetween(shopcoord, newmarker) / 1000).toFixed(2);
                                        }

                                      
                                       
                                           
                                        google.maps.event.addDomListener(window, 'load', initialize);
                                    </script>
                                    
                                    <div id="map-canvas" style="width:100%;height:285px;"></div>
       
   </head>
  
</html>

"""
        gmaps=gmaps.replace("z1", postcodetoverify)   #Replaces 'z1' in the HTML string above with the postcode that needs verifying
        self.webView.setHtml(gmaps)     #Sets the webview in the GUI to display the HTML Google Maps API in the string above          
        postcode=postcodetoverify
        try:
            from urllib.request import urlopen     #import modules to access a webpage
            response = urlopen("https://api.postcodes.io/postcodes/%s" %(postcode))  #Calls separate postcode API
        except:
            verifiedpostcode=False    #HTML webpage displayed in case of failure
            self.rangelabel.setText("Failed to determine eligibility.")
            self.webView.setHtml("""
                                 <center><h1>An Error Occured</h1></center>
                        
                                 <center><p>The Postcode Checker cannot find this address.</p></center>
                                 
                                 <p>This could be for a number of reasons:</p>
                                 <ul>
                                 <li>The postcode you entered is invalid - Check your postcode and try again.</li>
                                 <br>
                                 
                                 <li>You have no internet connection - Check your connection and try again.</li>
                                 </ul>
                                 """)

        else:
            full=response.read().decode("utf8")   #If response received, it is decoded
            import json   #import json module
            result1 = json.loads(full) 
            lat=result1['result']['latitude']   #Pick out logitude and latitude from data
            long=result1['result']['longitude']                
            from math import radians, cos, sin, asin, sqrt    #import maths functions                      
            def haversine(lon1, lat1, lon2, lat2):          #Function for haversine formula, used to work out distance between 2 coords
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1 
                dlat = lat2 - lat1 
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a)) 
                r = 6371 
                return c * r
            traveldist=haversine(long, lat, -0.73800, 51.6409256)        #Calls function and passes in parameters  
            if traveldist < 10:        #Sets verifiedpostcode to true/false depending on whether postcode is less than 10km away or not
                verifiedpostcode=True
            else:
                verifiedpostcode=False
            if verifiedpostcode==True:   #Changes label and button text depending on whether verified or not
                self.rangelabel.setText("Your postcode is within our delivery range! \n Distance from shop: %s km (10 km max)" %(format(traveldist, '.2f')))
                self.okbutton.setText("Continue")
            else:
                self.rangelabel.setText("Your postcode is outside our delivery range! \n We deliver up to 10 km, you are %s km away." %(format(traveldist, '.2f')))
                self.okbutton.setText("Go back")                            
    def ok(self):  #Back button
        self.hide()
        
def hasher(password):   #The hash function used to hash a password
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode()+password.encode()).hexdigest()+":"+salt

app = QtGui.QApplication(sys.argv)   
homescreen = SecondWindow(None)      #Loads the first window
homescreen.show()
app.exec_()
