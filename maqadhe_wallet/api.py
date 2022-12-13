import frappe,json
import requests
from frappe.utils import today

@frappe.whitelist()
def create_wallet_balance():
	import requests
	url = "https://apimaqadhe.ribox.me/rest/all/V1/walletsystem/wallet/list"
	payload={}
	headers = {
	}
	response = requests.request("GET", url, headers=headers, data=payload)
	resp = json.loads(response.text)
	l = []
	for i in resp["walletList"]:
		if not frappe.db.get_value("Wallet Balances",{"customer_name":i["customer_name"],"customer_mail":i["customer_mail"],"customer_id":i["customer_id"]}):
			print("no wallet balance")
			i["doctype"] = "Wallet Balances"
			customer = frappe.db.get_value("Customer",{"customer_name":i["customer_name"],"email_id":i["customer_mail"]})
			if customer:
				if not frappe.db.get_value("Customer",customer,"customer_id"):
							frappe.db.set_value("Customer",customer,"customer_id",i["customer_id"])
			else:
				customer = create_customer(i)
			i["customer"] = customer
			doc = frappe.get_doc(i)
			doc.insert(ignore_permissions = True)
			if doc.name:
				l.append("created = "+doc.name)
		else:
			wallet = frappe.db.sql('''select name from `tabWallet Balances` where customer_name = %s and customer_id = %s
			and customer_mail = %s and updated_at < %s ''',(i["customer_name"],i["customer_id"],i["customer_mail"],i["updated_at"]),as_dict=1)
			wallet = wallet[0]["name"] if wallet else None
			if wallet:
				doc = frappe.get_doc("Wallet Balances",wallet)
				doc.total_amount = i["total_amount"]
				doc.remaining_amount = i["remaining_amount"]
				doc.used_amount = i["used_amount"]
				doc.updated_at = i["updated_at"]
				doc.save(ignore_permissions = True)
				if doc.name:
					l.append("updated = "+doc.name)


	return l

def create_customer(order_doc):
	doc = frappe.get_doc(dict(
		doctype = "Customer",
		customer_name = order_doc['customer_name'],
		email_id = order_doc['customer_mail'],
		customer_id = order_doc['customer_id'],
		customer_group = frappe.db.get_value("Wallet Settings","Wallet Settings","customer_group"),
		territory = frappe.db.get_value("Wallet Settings","Wallet Settings","territory")
	)).insert(ignore_permissions = True)
	return doc.name

@frappe.whitelist()
def get_wallet_transactions():
	emails = frappe.db.sql('''select distinct(customer_mail) from `tabWallet Balances` ''',as_list=1)
	emails= [i[0] for i in emails]
	l=[]
	for i in emails:
		l.append(i)
		url = "https://apimaqadhe.ribox.me/rest/all/V1/walletsystem/transaction/"+str(i)
		payload={}
		headers = {}
		response = requests.request("GET", url, headers=headers, data=payload)
		resp = json.loads(response.text)
		if resp["transactionList"] == "No Data Found!":
			continue
		for j in resp["transactionList"]:
			cwb = frappe.db.sql('''select name from `tabConnector Wallet Transactions`  where email = %s
				and transaction_at = %s ''',(j["email"],j["transaction_at"]),as_dict=1)
			if not cwb:
				j["doctype"] = "Connector Wallet Transactions"
				j["customer_name"] = j["name"]
				j["mode_of_payment"] = j["payment_method"]
				del j["name"]
				j["api_status"] = j["status"]
				del j["status"]
				j["retry_limit"] = 5
				doc = frappe.get_doc(j)
				doc.insert(ignore_permissions = True)
				l.append(doc.name)
				l.append("         ")
	return l
	
@frappe.whitelist()
def create_jv_for_transactions(tsn_id = None):
	filter = ""
	if tsn_id:
		filter  += "and name = '{0}' ".format(tsn_id)
	cwb = frappe.db.sql('''select sender_type,mode_of_payment,amount,customer_id,name,retry_limit,is_sync,transaction_note from `tabConnector Wallet Transactions` where is_sync = 0
			and status = "Pending" and retry_limit > 0 {0} order by creation asc limit 10'''.format(filter),as_dict =1)
	pay_mode = frappe.db.get_value("Wallet Settings","Wallet Settings","default_mode_of_payment")
	for i in cwb:
		if i["is_sync"] or not i["amount"]:
				continue
		frappe.db.set_value("Connector Wallet Transactions",i["name"],"retry_limit",int(i["retry_limit"])-1)
		mod_account = ""
		if i["sender_type"] == "Recharge wallet":
			mod_account = frappe.db.get_value("Mode of Payment Account",{"parent":pay_mode},"default_account")
		elif i["sender_type"] == "Admin credit" or i["sender_type"] == "Admin debit" or i["sender_type"] == "Refund order":
			frappe.errprint("Refund order")
			mod_account = frappe.db.get_value("Wallet Settings","Wallet Settings","adjustment_account")
		else:
			continue
		doc = frappe.new_doc("Journal Entry")
		doc.posting_date = frappe.utils.today()
		db_amt = 0
		cr_amt = 0
		db_amt = i["amount"]
		if i["sender_type"] == "Admin debit":
			db_amt = 0
			cr_amt = i["amount"]
		doc.append("accounts",{
			"account":mod_account,
			"debit_in_account_currency":db_amt,
			"credit_in_account_currency":cr_amt
		})
		customer_account = frappe.db.get_value("Wallet Settings","Wallet Settings","account")
		customer = frappe.db.get_value("Customer",{"customer_id":i["customer_id"]})
		ref_doc = i["transaction_note"]
		doc.append("accounts",{
			"account":customer_account,
			"party_type":"Customer",
			"party":customer,
			"credit_in_account_currency":db_amt,
			"debit_in_account_currency":cr_amt,
			"user_remark":ref_doc
		})
		doc.save(ignore_permissions = True)
		if doc.name:
			sje = frappe.db.get_value("Wallet Settings","Wallet Settings","submit_journal_entry")
			if sje == "1":
				doc.submit()
			frappe.db.set_value("Connector Wallet Transactions",i["name"],"reference_id",doc.name)
			frappe.db.set_value("Connector Wallet Transactions",i["name"],"is_sync",1)
			frappe.db.set_value("Connector Wallet Transactions",i["name"],"status","Synced")
			link = "<a href='/desk#Form/Journal%20Entry/{0}'>{0}</a>".format(doc.name)
			frappe.msgprint("Transaction synced against {0}".format(link) )

@frappe.whitelist()
def use_wallet(doc):
	amount = 0
	sn = frappe.get_doc("Sales Invoice",doc)
	for i in sn.sales_order_payment:
		if i.is_sync and i.used_wallet_amount == 0:
			frappe.throw("JV already Created")
		amount = i.used_wallet_amount
	if amount<0:
		amount = abs(amount)
		new_doc = frappe.new_doc("Journal Entry")
		new_doc.posting_date = frappe.utils.today()
		customer = sn.customer
		customer_wallet = frappe.db.get_value("Wallet Settings","Wallet Settings","account")
		sales_account = frappe.db.get_value("Wallet Settings","Wallet Settings","sales_account")
		db_amt = cr_amt = 0
		db_amt = amount
		new_doc.append("accounts",{
                        "account":customer_wallet,
			"party_type":"Customer",
			"party":customer,
                        "debit_in_account_currency":db_amt,
                        "credit_in_account_currency":cr_amt
                })
		new_doc.append("accounts",{
                        "account":sales_account,
                        "party_type":"Customer",
                        "party":customer,
                        "credit_in_account_currency":db_amt,
                        "debit_in_account_currency":cr_amt,
                        "reference_type":"Sales Invoice",
			"reference_name" : doc
                })
		new_doc.save(ignore_permissions = True)
		if new_doc.name:
			for i in sn.sales_order_payment:
				i.used_wallet_amount = 0
				i.is_sync = 1
			sn.save(ignore_permissions=True)
			if sn.reference_num:
				frappe.db.sql('''update `tabConnector Wallet Transactions` set is_sync=1 ,status = "Synced" where sender_type = "Use wallet" and order_increment_id = %s''',sn.reference_num)
				frappe.db.commit()
			link = "<a href='/desk#Form/Journal%20Entry/{0}'>{0}</a>".format(new_doc.name)
			frappe.msgprint("JV created for Wallet Amount - {0}".format(link))
		return 0

