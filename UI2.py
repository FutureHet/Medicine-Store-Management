import cx_Oracle
import datetime
import copy
import sys

def print_table_content():
	print('Which table you want to print: ')
	inp = input().upper()
	c.execute("select * from " + inp)
	print(schema[inp])
	for i in c:
		print(i)

def user_info():
	print('Enter your user id: ')
	user_id = int(input())
	c.execute("select * from user_data where user_id = :var",var=user_id)
	for row in c:
		print(row)
	print()
	print("Your bill details:-")
	c.execute("select * from bill_info where user_id = :var",var=user_id)
	print(schema['BILL_INFO'])
	for row in c:
		print(row)
	print()

def create_user():
	c.execute('select count(*) from user_data')
	user_id = 0
	for i in c:
		user_id = int(i[0])+1
	f_name = input('Enter your first name: ')
	l_name = input('Enter your last name: ')
	add = input('Enter your Area: ')
	m_no = int(input('Enter your mobile no.: '))
	email = input('Enter your email: ')
	try:
		c.execute("insert into user_data values(:o,:p,:q,:r,:s,:t)",o=user_id,p=f_name,q=l_name,r=add,s=m_no,t=email)
	except:
		print(sys_exc_info())
		c.execute('rollback')
	else:
		print('Successfully Inserted')
		c.execute('commit')

def find_medicine_name():
	print('Enter which Medicine you want:')
	med_name = '%'+input().upper()+'%'
	c.execute('select * from medicine where upper(product_name) like :var',var=med_name)
	for i in c:
		print(i)

def find_medicine_content():
	print('Enter which content you require in medicine:')
	content = '%'+input().upper()+'%'
	c.execute("select * from medicine m where m.productid in (select productid from con_med_rel c where c.content_id in (select content_id from content where upper(content.content_name) like :var))",var=content)
	for i in c:
		print(i)

def add_medicine():
	print('Enter product id: ')
	pid = input()
	print('Enter product name: ')
	pname = input()
	print('Enter type of that medicine: ')
	ptype = input()
	print('Enter weight of medicine: ')
	pweight = input()
	try:
		c.execute("insert into medicine values(:o,:p,:q,:r)",o=pid.upper(),p=pname.capitalize(),q=ptype.capitalize(),r=pweight)
	except:
		print(sys.exc_info())
		c.execute('rollback')
	else:
		print('Successfully Inserted')
		c.execute('commit')

def add_content():
	print('Enter content id:')
	cid = input()
	print('Enter content name:')
	cname = input()
	print('Enter content type:')
	ctype = input()
	try:
		c.execute("insert into medicine values(:o,:p,:q)",o=cid.upper(),p=cname.capitalize(),q=ctype.capitalize())
	except:
		print(sys_exc_info())
		c.execute('rollback')
	else:
		print('Successfully Inserted')
		c.execute('commit')		

def create_bill():
	bill_no_gen = 0
	data_update=[]
	rows = c.execute('select count(*) from Bill_info')
	for i in rows:
		bill_no_gen = i[0]+1
	sid = int(input('Enter Shopkeeper ID:'))
	sname = ""
	c.execute("select name from shopkeeper where shopkeeperid = :var",var=sid)
	for x in c:
		sname = x[0]
	uid = int(input('Enter User ID:'))
	uname = ""
	c.execute("select first_name,last_name from user_data where user_id = :var",var=uid)
	for x in c:
		sname = x[0]+' '+x[1]
	
	print('Press Z when Bill generation is completed')
	while True:
		print('Enter product_id:')
		product_id = input()
		productname=""
		if(product_id == 'z' or product_id == 'Z'):
			break
		c.execute("select product_name from medicine where productid = :var",var=str(product_id))
		for x in c:
			productname = x[0]
		print('Product Name:',productname,end='\n\n')
		strt = "select batchid,mrp,stock,discount from batch where productid = '%s' and stock != 0"%(product_id)
		rows = c.execute(strt)
		for i in rows:
			print(i[2],type(i[2]))
		if(rows.rowcount == 0):
			print("Sorry We don't have Product Right Now")
		else:
			qty = int(input('Enter Total Quantity Required:'))
			main_qty = qty
			c.execute(strt)
			full_data=[]
			for i in c:
				full_data.append(i)
			for i in full_data:
				temp = int(i[2])-qty;
				if(temp < 0):
					qty = -temp
					temp = 0
					main_qty = main_qty-qty
				else:
					main_qty = qty
					qty = 0
				strt = "update batch set stock='%s' where batchid='%s' and Productid='%s'"%(temp,str(i[0]),product_id)
				c.execute(strt)
				data_update.append([bill_no_gen,str(i[0]),product_id,i[1]*(1-i[3]),main_qty,1-i[3],productname])
				#c.execute('commit')
				if(qty == 0):
					break
			if(qty != 0):
				print("We don't Have stock for your full requiement sorry!!",qty)
	total_qty=0
	total_sale=0
	total_MRP=0
	for i in data_update:
		strt = "insert into bill_summary values ('%s','%s','%s','%s','%s')"%(i[0],i[1],i[2],i[3],i[4])
		c.execute(strt)
		#print(strt)
		total_qty += i[4]
		total_sale += i[4]*i[3]
		total_MRP += i[4]*i[3]/i[5]
	print(data_update)
	total_MRP = total_MRP-total_sale
	c.execute("insert into bill_info values (:o,:p,:q,:r,:s,:t,:u)",o=bill_no_gen,p=total_sale,q=total_MRP,r=total_qty,s=sid,t=uid,u=datetime.datetime.now())
	#print(strt)
	print("===========================\nBill Generated")
	print("==============================================")
	print("Product Name","Batch","Qty","Price","Total Price",sep='\t')
	print("==============================================================")
	for i in data_update:
		print(i[6],i[1],i[4],i[3],i[4]*i[3],sep='\t')
	print("====================================================")
	print('Patient Name:',uname)
	print('Bill No:',bill_no_gen)
	print('Total Quantity:',total_qty)
	print('Total Bill Amount:',total_sale)
	print('Total Savings:',total_MRP)
	print('Sold By:',sname)
	print(data_update)	
	c.execute('commit')
    
def remove_old_meds():
    data_update=[]
    c.execute('select batchid,productid,mfg_date,add_months(mfg_date,best_before_months) expiry_date,stock from batch where add_months(mfg_date,best_before_months) < (select sysdate from dual) and stock!=0')
    for i in c:
        data_update.append(i)
    print('BatchID\tProductID Expiry Date\tNew Stock')
    print("========================================================")
    try:
        for i in data_update:
            print(i[0],i[1],str(i[3])[:10],'0',sep='\t')
            c.execute('update batch set stock=0 where batchid=:var1 and productid=:var2',var1=i[0],var2=i[1])
    except:
        print(sys.exc_info())
        c.execute('rollback')
    else:
        c.execute('commit')
dsn_tns = cx_Oracle.makedsn('immortal', '1521', service_name='XE')
conn = cx_Oracle.connect(user=r'dbms_project', password='dbms_project', dsn=dsn_tns)
c = conn.cursor()

schema={'USER_DATA':[],'MEDICINE':[],'CONTENT':[],'FORM':[],
'CON_MED_REL':[],'SHOPKEEPER':[],'SUPPLIER':[],
'MANUFACTURER':[],'BATCH':[],'BILL_INFO':[],'BILL_SUMMARY':[]}

for i in schema.keys():
	c.execute('select * from '+i)

	for rows in c.description:
		schema[i].append(rows[0])

print('Welcome sir 😊,\nHow can we help you\n')
while(True):
	print("\n1.Show the data of table\n2.Show user information\n3.Create new User\n4.Find Medicine\n5.Find Medicine Based On content\n6.Bill generation\n7.Add new medicine\n8.Add new content\n9.Remove Old Medicine\n10.Quit")
	i = int(input())
	if (i==1):
		print_table_content()
	elif(i==2):
		user_info()
	elif(i==3):
		create_user()
	elif(i==4):
		find_medicine_name()
	elif(i==5):
		find_medicine_content()
	elif(i==6):
		try:
			create_bill()
		except:
			c.execute('rollback')
			print('Some Errors Might Have Occured')
		else:
			c.execute('commit')
	elif(i==7):
		add_medicine()
	elif(i==8):
		add_content()
	elif(i==9):
		remove_old_meds()
	elif(i==10):
		break
	else:
		print("Please enter valid input:")

print("Thank you, sir.👋")