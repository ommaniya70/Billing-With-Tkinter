# Import Statements
from tkinter import *
import mysql.connector
import sys
from datetime import date
from tkinter import ttk
from tkcalendar import Calendar
from tkinter import messagebox
import pandas as pd
import jinja2
import pdfkit
import PrintInvoice

# Database Connection
try:
    db = mysql.connector.connect(
        host = "localhost",
        user="root",
        database="data"
    )
except Exception as error:
    messagebox.showerror("Error","SQL Database is not ready to use.")
    sys.exit()
mycursor = db.cursor()

##########################################################################################################################################
# Creating a Stage named root and initializing all the properties
root = Tk()
root.title("Invoice Generator")
root.geometry("1100x700")

# Defining all the variables
dateAuto = StringVar()
dateByUsrOrNot = IntVar()
clearNameOrNot = IntVar()
# PIWeightByUsrOrNot = IntVar()
# PITopByUsrOrNot = IntVar()
PIWeightOrPITopByUsrOrNot = IntVar()
rootDiv1WeightFieldVar = StringVar()
PIWeightFieldTextVar = float()
count = 0

################################################################################################################################# 
# Defining all the functions


# Fixed Functions

def CalculateTotalWhenPIWeightAndPITopZero(Dimond,Weight,Top):
    # Edit for top>0
    Weight = float(Weight)
    Top = int(Top)
    Dimond = int(Dimond)
    Weight = Weight/Dimond
    total = 0
    if(Weight >= 0.15):
        total += Weight
        if(Top > 1):
            for i in range(2,Top+1):
                Weight = Weight - (Weight*20)/100
                total += Weight
    
    elif(Weight < 0.15):
        total = Top*Dimond

    return total

def CalculateTotalWhenPIWeightOrPITopIsNotZero(Dimond,Weight,PIWeight,PITop,Top):
    total = 0
    Dimond = int(Dimond)
    Weight = float(Weight)
    PIWeight = float(PIWeight)
    PITop = int(PITop)
    Top = int(Top)
    Weight = Weight/Dimond
    if(Weight >= 0.15):
        if(PIWeight != 0 and PITop == 0):
            PIWeight = PIWeight - (PIWeight*20)/100
            total = PIWeight
            for i in range(1,Top):
                PIWeight = PIWeight - (PIWeight*20)/100
                total += PIWeight
        return total

    elif(Weight < 0.15):
        if(PIWeight == 0 and PITop != 0):
            total = Dimond*Top
    return total

# Function to create treeview but pack scroll bar before use this function
def createTreeView(tv,scrollbar):
    # Defining Columns
    tv['columns'] = ("Id","Date","Name", "Dimond","Weight","PI Top","PI Weight","Top","Total")

    # Formate columns
    tv.column('#0',width=0,anchor=CENTER)
    tv.column('Id',anchor=CENTER,width=90)
    tv.column('Date',anchor=CENTER,width=90)
    tv.column('Name',anchor=CENTER,width=150)
    tv.column('Dimond',anchor=CENTER,width=70)
    tv.column('Weight',anchor=CENTER,width=70)
    tv.column('PI Weight',anchor=CENTER,width=70)
    tv.column('PI Top',anchor=CENTER,width=70)
    tv.column('Top',anchor=CENTER,width=70)
    tv.column('Total',anchor=CENTER,width=100)

    # Headings
    tv.heading('#0',text="",anchor=CENTER)
    tv.heading('Id',text="Id",anchor=CENTER)
    tv.heading('Date',text="Date",anchor=CENTER)
    tv.heading('Name',text="Name",anchor=CENTER)
    tv.heading('Dimond',text="Dimond",anchor=CENTER)
    tv.heading('Weight',text="Weight",anchor=CENTER)
    tv.heading('PI Weight',text="PI Weight",anchor=CENTER)
    tv.heading('PI Top',text="PI Top",anchor=CENTER)
    tv.heading('Top',text="Top",anchor=CENTER)
    tv.heading('Total',text="Total",anchor=CENTER)
 
    # Calling pack method w.r.to vertical
    tv.configure(yscrollcommand=scrollbar.set)

    scrollbar.configure(command=tv.yview)
    tv.configure(selectmode="extended")
    
    tv.grid(row=0,column=1,padx=20,rowspan=2,columnspan=9)

# Function to check number is float or not
def validateWeight(num):
    val = 1
    for i in num:
        if(i == '.' or i.isdigit()):
            pass
        else:
            val = 0
            break
    return val

# Function to disable and enable Date field
def setDateManually():
    if(dateByUsrOrNot.get() == 0):
        rootDiv1DateField.config(state= "disabled")
    else:
        rootDiv1DateField.config(state="normal")

def enableDisablePIWeightOrPITopField():
    if((rootDiv1WeightField.get()=="") or (PIWeightOrPITopByUsrOrNot.get()==0)):
        rootDiv1PIWeightField.config(state="normal")
        rootDiv1PIWeightField.delete(0,END)
        rootDiv1PIWeightField.insert(0,"0")
        rootDiv1PIWeightField.config(state="disabled")
        rootDiv1PITopField.config(state="normal")
        rootDiv1PITopField.delete(0,END)
        rootDiv1PITopField.insert(0,"0")
        rootDiv1PITopField.config(state="disabled")
    else:
        weight = float(rootDiv1WeightField.get())
        dimond = int(rootDiv1DimondField.get())
        weight = weight/dimond
        if(weight > 0.15):
            rootDiv1PIWeightField.config(state="normal")
            rootDiv1PIWeightField.delete(0,END)
            # rootDiv1PIWeightField.insert(0,rootDiv1WeightField.get())
            # rootDiv1PIWeightField.config(state="disabled")
        else:
            rootDiv1PITopField.config(state="normal")
            rootDiv1PITopField.delete(0,END)

# Function for Validating Name
def validateName(name):
    val = 1
    for i in name:
        if((i>='a' and i<='z') or (i>='A' and i<='Z') or (i==" ")):
            val = 1
        else:
            val = 0
            break
    return val

def clearSelectionFromTreeview(tv):
    if len(tv.selection()) > 0:
        for i in tv.selection():
            tv.selection_remove(i)
    else:
        messagebox.showerror("Error","Cannot find any Selection")
        

def setDate():
    today = date.today()
    today = today.strftime("%d/%m/%y")
    dateAuto.set(today)

def clearName():
    if(clearNameOrNot.get() == 1):
        rootDiv1NameField.delete(0,END)

def reinitializeAllFields():
    # Reinitializing all the fields
    clearName()
    dateForInsert = ""
    nameForInsert = ""
    dimondForInsert = ""
    weightForInsert = ""
    topForInsert = ""
    PIWeightForInsert = ""
    PITopForInsert = ""
    totalForInsert = 0
    rootDiv1DimondField.delete(0,END)
    rootDiv1TopField.delete(0,END)
    rootDiv1WeightField.delete(0,END)
    rootDiv1PIWeightField.delete(0,END)
    rootDiv1PITopField.delete(0,END)
    dateByUsrOrNot.set(0)
    clearNameOrNot.set(0)
    PIWeightOrPITopByUsrOrNot.set(0)
    PIWeightOrPITopByUsrOrNot.set(0)
    enableDisablePIWeightOrPITopField()
    setDate()
    setDateManually()

def validateInputFieldsForInsert(dateForInsert,nameForInsert,dimondForInsert,weightForInsert,PIWeightForInsert,PITopForInsert,topForInsert):

    if(len(dateForInsert) != 0 and len(nameForInsert) != 0 and len(dimondForInsert) != 0 and len(weightForInsert) != 0 and len(PIWeightForInsert) != 0 and len(PITopForInsert) != 0 and len(topForInsert) != 0):

        if((validateName(nameForInsert)==1) and dimondForInsert.isnumeric() and (validateWeight(weightForInsert)==1) and (validateWeight(PIWeightForInsert)==1) and PITopForInsert.isnumeric() and topForInsert.isnumeric()):
            return True
        else:
            return False
    else:
        return False

def InsertRecord(*args):
    mycursor.execute("CREATE TABLE IF NOT EXISTS Customer(Id int PRIMARY KEY AUTO_INCREMENT,Date VARCHAR(8),Name VARCHAR(50),Dimond smallint,Weight float(4),PI_Weight float(4),PI_Top int,Top tinyint,Total int)")
    dateForInsert = rootDiv1DateField.get().strip()
    nameForInsert = rootDiv1NameField.get().strip()
    dimondForInsert = rootDiv1DimondField.get().strip()
    weightForInsert = rootDiv1WeightField.get().strip()
    PIWeightForInsert = rootDiv1PIWeightField.get().strip()
    PITopForInsert = rootDiv1PITopField.get().strip()
    topForInsert = rootDiv1TopField.get().strip()

    if((validateInputFieldsForInsert(dateForInsert,nameForInsert,dimondForInsert,weightForInsert,PIWeightForInsert,PITopForInsert,topForInsert))==1):

        PITopForInsert = int(PITopForInsert) * int(dimondForInsert)
        PITopForInsert = str(PITopForInsert)

        temp = float(weightForInsert)
        temp1 = 0
        temp3 = int(PIWeightForInsert)
        for i in range(0,temp3):
            temp1 += temp
            temp = temp - (temp*20)/100
        weightForInsert = temp1

        if(PITopForInsert=="0" and PIWeightForInsert=="0"):
            totalForInsert = CalculateTotalWhenPIWeightAndPITopZero(dimondForInsert,weightForInsert,topForInsert)
        else:
            totalForInsert = CalculateTotalWhenPIWeightOrPITopIsNotZero(dimondForInsert,weightForInsert,PIWeightForInsert,PITopForInsert, topForInsert)
            
        totalForInsert = round(totalForInsert,4)

        mycursor.execute("INSERT INTO Customer (Date,Name,Dimond,Weight,PI_Weight,PI_Top,Top,Total) Values(%s,%s,%s,%s,%s,%s,%s,%s)",(dateForInsert,nameForInsert,dimondForInsert,weightForInsert,PITopForInsert,PIWeightForInsert,topForInsert,totalForInsert))
        db.commit()
        
        # Delete last two grandtotals just in case add data is pressed after pressing grand total
        DeleteGrandTotalForRootTV()

        # Insert Records from fields to Tree View
        # Fetching the last record of Database
        global count
        x = mycursor.execute("SELECT * FROM Customer ORDER BY ID DESC LIMIT 1")
        for i in mycursor:
            pass

        rootTV.insert(parent='',index='end',iid=count,values=(i[0],dateForInsert,nameForInsert,dimondForInsert,weightForInsert,PITopForInsert,PIWeightForInsert,topForInsert,totalForInsert))
        count += 1

        reinitializeAllFields()
        rootDiv1ErrorLabel.config(text="Data Added Successfully",foreground="green",font=("Arial 13 bold"))
        rootDiv1DimondField.focus_set()

    else:
        messagebox.showerror("Error", "Enter Valid Information")

def DeleteGrandTotal(tv):
    for i in tv.get_children():
        x = tv.item(i)['values']
        if(x[2] == " "):
            tv.delete(i) 

def GrandTotal(tv):
    DeleteGrandTotalForRootTV() 
    totalPITop = 0
    totalPIWeight = 0
    total1 = 0.0
    total2 = 0.0
    temp = 0 
    for i in tv.get_children():
        x = tv.item(i)['values']
        temp = float(x[4])/int(x[3])
        p = float(x[8])
        if(temp <= 0.15):
            total1 += p
        else:
            total2 += p

        totalPITop += x[5]
        totalPIWeight +=x[6]

        temp += 1
    tv.insert(parent='',index='end',iid=temp,values=(" "," "," "," "," "," "," ","Total1",total1))
    tv.insert(parent='',index='end',iid=temp+1,values=(" "," "," "," "," ",totalPITop,totalPIWeight,"Total2",total2))

def DeleteRecordFromTreeView(tv):
    temp = tv.selection()
    if(len(temp) == 0):
        messagebox.showerror("Error","No Data Selected")
    else:
        value = messagebox.askquestion("Confirm","Are you sure want to delete the data ?")
        if(value == "yes"):
            for i in temp:
                tv.delete(i)

def DeleteRecordFromTreeViewAndDatabase(tv):
    x = []
    temp = tv.selection()
    
    # checks the length of tuple and displays message
    if(len(temp) == 0):
        messagebox.showerror("Error","No Data Selected")
    else:
        value = messagebox.askquestion("Confirm","Are you sure want to delete data ?")
        if(value == "yes"):
            for i in temp:
                x.append(tv.item(i)['values'][0])
                tv.delete(i)
            for i in x:
                query = "DELETE FROM Customer WHERE Id = %s"
                data = (i,)
                mycursor.execute(query,data)
                db.commit()
            x.clear()


def GenerateInvoice(tv):
    temp = 1
    indexList = []
    DimondList = []
    WeightList = []
    PITopList = []
    PIWeightList = []
    PITopList = []
    TopList = []
    TotalList = []
    for i in tv.get_children():
        x = tv.item(i)['values']
        indexList.append(temp)
        DimondList.append(x[3])
        WeightList.append(x[4])
        PITopList.append(x[5])
        PIWeightList.append(x[6])
        TopList.append(x[7])
        TotalList.append(x[8])
        temp += 1
    
    df = pd.DataFrame(list(zip(DimondList,WeightList,PITopList,PIWeightList,TopList,TotalList)),columns=['Dimond','Weight','PI Top','PIWeight','Top','Total'],index=indexList)
    df.index.name = 'Sr. No.'
    df.to_excel("temp.xlsx")

    PrintInvoice.CreatePDF()

def ImportRec():
    # Initializing all the variables
    startingDateVar = ""
    endingDateVar = ""
    nameVar = ""
    count = 0

    # Defining Functions
    def DeleteRecordFromRoot1TreeView():
        DeleteRecordFromTreeView(root1TV)

    def DeleteRecordFromRoot1TreeViewAndDatabase():
        DeleteRecordFromTreeViewAndDatabase(root1TV)

    def GenerateInvoiceForRoot1TV():
        GenerateInvoice(root1TV)

    def ResetAllForRoot1TV():
        if(len(root1TV.get_children()) == 0):
            messagebox.showerror("Error","No Data Found")
        else:
            value = messagebox.askquestion("Confirm","Are You sure Want to Delete All the table Data ?")
            if(value == "yes"):
                deleteAllRecordFromTreeView(root1TV)
    
    def clearSelectionFromRoot1Treeview():
        clearSelectionFromTreeview(root1TV)

    def GetData(*args):
        # Clear all the Date Fields 
        root1StartingDateField.config(state="normal")
        root1StartingDateField.delete(0,END)
        root1StartingDateField.config(state="disabled")

        root1EndingDateField.config(state="normal")
        root1EndingDateField.delete(0,END)
        root1EndingDateField.config(state="disabled")

        startingDateVar = ""
        endingDateVar = ""
        nameVar = ""
        value = "yes"

        ##################################################################################################################################
        
        temp = startingDate.selection_get()
        root1StartingDateField.config(state="normal")
        root1StartingDateField.insert(0,temp.strftime("%d/%m/%y"))
        root1StartingDateField.config(state="disabled")

        temp = EndingDate.selection_get()
        root1EndingDateField.config(state="normal")
        root1EndingDateField.insert(0,temp.strftime("%d/%m/%y"))
        root1EndingDateField.config(state="disabled")

        startingDateVar = root1StartingDateField.get()
        endingDateVar = root1EndingDateField.get()
        nameVar = root1NameField.get().strip()

        def validateAllForTreeView():
            if(len(nameVar) !=0 and len(startingDateVar) != 0 and len(endingDateVar) != 0 and validateName(nameVar) == 1):
                return True
            else:
                return False

        if(validateAllForTreeView() == True):
            if(len(root1TV.get_children()) != 0):
                value = messagebox.askquestion("Confirm","All the previous Table Data will be lost Do You Want to Continue ?")
            if(value == "yes"):
                deleteAllRecordFromTreeView(root1TV)
                query = '''SELECT * FROM Customer WHERE (Date BETWEEN %s AND %s) AND Name = %s'''
                data = (startingDateVar,endingDateVar,nameVar,)
                mycursor.execute(query,data)
                global count
                for i in mycursor:
                    root1TV.insert(parent='',index='end',iid=count,values=(i[0],i[1],i[2],i[3],i[4],i[5],i[6]))
                    count += 1
                
                if(len(root1TV.get_children()) == 0):
                    messagebox.showinfo("Information","No such data found")
        
        else:
            messagebox.showerror("showerror", "Enter Valid Information")
            

    # Creating a Stage named root and initializing all the properties
    root1 = Tk()
    root1.title("Import Records")
    root1.geometry("1100x700")


    root1TV = ttk.Treeview(root1)
    root1ScrollBar = Scrollbar(root1,orient=VERTICAL,width=30)
    root1ScrollBar.grid(row=1,column=10,padx=20,sticky=W,ipady=90,pady=80)
    createTreeView(root1TV,root1ScrollBar)

    # Creating Menu
    root1File = Menu(root1)
    root1submenu = Menu(root1File,tearoff=0)
    root1submenu.add_command(label="Print Now",command=GenerateInvoiceForRoot1TV)
    root1submenu.add_command(label="Delete Record Permanently",command=DeleteRecordFromRoot1TreeViewAndDatabase)
    root1submenu.add_separator()
    root1submenu.add_command(label="Remove Selection",command=clearSelectionFromRoot1Treeview)
    root1submenu.add_command(label="Reset All",command=ResetAllForRoot1TV)
    root1.config(menu=root1File)
    root1File.add_cascade(label="File",menu=root1submenu)

    root1DeleteRecordButton = Button(root1,text="Delete Record",command=DeleteRecordFromRoot1TreeView)
    root1DeleteRecordButton.grid(row=4,column=10)

    root1StartingDateLabel = Label(root1,text="Select Starting Date")
    root1StartingDateLabel.grid(row=2,column=2)

    today = date.today()

    startingDate = Calendar(root1, selectmode = 'day',year = today.year, month = today.month,day = today.day)
    startingDate.grid(row=3,column=2,padx=20)

    root1StartingDateField = Entry(root1,state="disabled")
    root1StartingDateField.grid(row=6,column=2,padx=20,pady=10)

    root1EndingDateLabel = Label(root1,text="Select Ending Date")
    root1EndingDateLabel.grid(row=2,column=5)
    root1EndingDateField = Entry(root1,state="disabled")
    root1EndingDateField.grid(row=6,column=5,padx=20,pady=10)

    EndingDate = Calendar(root1, selectmode = 'day',year = today.year, month = today.month,day = today.day)
    EndingDate.grid(row=3,column=5,padx=20)


    root1NameLabel = Label(root1,text="Name")
    root1NameLabel.grid(row=2,column=7,padx=30,columnspan=2)

    root1NameField = Entry(root1)
    root1NameField.grid(row=2,column=9,columnspan=2)

    root1GetDataButton = Button(root1,text="Get Data",command=GetData)
    root1GetDataButton.grid(row=3,column=10,sticky="n",pady=20)
    root1.bind('<Return>',GetData)
    root1.mainloop()

def deleteAllRecordFromTreeView(tv):
    global count
    for record in tv.get_children():
        tv.delete(record)
    count = 0


####################################################################################################################
# Mandatory Function Call
setDate()

# Calling Functions
def ResetAllForRootTV():
    if(len(rootTV.get_children()) == 0):
        messagebox.showerror("Error","No data found")
    else:
        value = messagebox.askquestion("Confirm","Are you sure want to clear the table")
        if(value == "yes"):
            deleteAllRecordFromTreeView(rootTV)

def DeleteRecordFromRootTreeView():
    DeleteRecordFromTreeView(rootTV)

def DeleteRecordFromRootTreeViewAndDatabase():
    DeleteRecordFromTreeViewAndDatabase(rootTV)

def clearSelectionFromRootTreeview():
    clearSelectionFromTreeview(rootTV)

def GrandTotalForRootTV():
    GrandTotal(rootTV)

def DeleteGrandTotalForRootTV():
    DeleteGrandTotal(rootTV)

def GenerateInvoiceForRootTV():
    GenerateInvoice(rootTV)

##########################################################################################################################################
# Creating Widgets as per the requirement
# Creating all the required Entry Fields and Buttons

# Creating root Tree view
rootTV = ttk.Treeview(root)

# Creating Scroll bars
rootScrollBar = Scrollbar(root,orient=VERTICAL,width=30)
rootScrollBar.grid(row=1,column=11,sticky=W,ipady=90,pady=80)
createTreeView(rootTV,rootScrollBar)

# Creating Menu
rootFile = Menu(root)
rootsubmenu = Menu(rootFile,tearoff=0)
rootsubmenu.add_command(label="Print Now",command=GenerateInvoiceForRootTV)
rootsubmenu.add_command(label="Import Records",command=ImportRec)
rootsubmenu.add_separator()
rootsubmenu.add_command(label="Delete Permanently",command=DeleteRecordFromRootTreeViewAndDatabase)
rootsubmenu.add_command(label="Remove Selection",command=clearSelectionFromRootTreeview)
rootsubmenu.add_command(label="Reset All",command=ResetAllForRootTV)
root.config(menu=rootFile)
rootFile.add_cascade(label="File",menu=rootsubmenu)

# Creating Fields
rootDiv1DateField = Entry(root,textvariable=dateAuto,state="disabled")
rootDiv1NameField = Entry(root)
rootDiv1DimondField = Entry(root,width=6)
rootDiv1WeightField = Entry(root,width=6)

rootDiv1PIWeightField = Entry(root,width=6,textvariable=PIWeightFieldTextVar)
rootDiv1PIWeightField.insert(0,"0")
rootDiv1PIWeightField.config(state="disabled")

rootDiv1PIWeightChkBox = Checkbutton(text="",variable=PIWeightOrPITopByUsrOrNot,command=enableDisablePIWeightOrPITopField)

rootDiv1PITopField = Entry(root,width=6)
rootDiv1PITopField.insert(0,"0")
rootDiv1PITopField.config(state="disabled")

# rootDiv1PITopChkBox = Checkbutton(text="",variable=PITopByUsrOrNot,command=enableDisablePITopField)

rootDiv1TopField = Entry(root,width=6)


# Creating Buttons
rootDiv1AddDataButton = Button(root,text="Add Data",command=InsertRecord)
root.bind('<Return>', InsertRecord)
rootDiv1GenerateButton = Button(root,text="Grand Total",command=GrandTotalForRootTV)
rootDiv1DeleteRecordButton = Button(root,text="Delete Record",command=DeleteRecordFromRootTreeView)
# rootDiv1DeleteRecordPermanentButton = Button(root,text="Delete Permanently",command=DeleteRecordFromRootTreeViewAndDatabase)

# Creating All the Labels and CheckBoxes
rootDiv1ErrorLabel = Label(root,text="")
rootDiv1DateLabel = Label(root,text="Date")
rootDiv1DateChkBox = Checkbutton(text="Set Date Manually",variable=dateByUsrOrNot,command=setDateManually)
rootDiv1NameLabel = Label(root,text="Name")
rootDiv1DimondLabel = Label(text="Dimonds")
rootDiv1WeightLabel = Label(text="Weight")
rootDiv1PIWeightLabel = Label(text="PI Weight")
rootDiv1PITopLabel = Label(text="PI Top")
rootDiv1TopLabel = Label(text="Top ")
rootDiv1NameChkBox = Checkbutton(text="Clear Name",variable=clearNameOrNot)




# Packing all the widgets
rootDiv1DateLabel.grid(row=3,column=0,pady=5,padx=20)
rootDiv1DateField.grid(row=3,column=1)
rootDiv1DateChkBox.grid(row=4,column=1,sticky=W,pady=10)

rootDiv1NameLabel.grid(row=3,column=2,pady=5,sticky=E)
rootDiv1NameField.grid(row=3,column=3,padx=5,sticky=W)
rootDiv1NameChkBox.grid(row=4,column=3,sticky=W,ipadx=0)

rootDiv1DimondLabel.grid(row=3,column=4,padx=8,pady=5)
rootDiv1DimondField.grid(row=3,column=5)

rootDiv1WeightLabel.grid(row=3,column=6,padx=8,pady=5)
rootDiv1WeightField.grid(row=3,column=7)

rootDiv1PIWeightLabel.grid(row=3,column=8,padx=8,pady=5)
rootDiv1PIWeightField.grid(row=3,column=9,padx=5,pady=5)

rootDiv1PIWeightChkBox.grid(row=4,column=9)

rootDiv1PITopLabel.grid(row=3,column=10,padx=8,pady=5)
rootDiv1PITopField.grid(row=3,column=11,padx=5,pady=5)

# rootDiv1PITopChkBox.grid(row=4,column=11)

rootDiv1TopLabel.grid(row=3,column=12,padx=8,pady=5)
rootDiv1TopField.grid(row=3,column=13)


rootDiv1AddDataButton.grid(row=5,column=1,sticky=W,pady=40,padx=20)
rootDiv1GenerateButton.grid(row=5,column=2,sticky=W,padx=20,pady=40)
rootDiv1DeleteRecordButton.grid(row=5,column=3,padx=20)
# rootDiv1DeleteRecordPermanentButton.grid(row=5,column=3,sticky=W,padx=20,pady=40)



# Go Back to event loop
root.mainloop()