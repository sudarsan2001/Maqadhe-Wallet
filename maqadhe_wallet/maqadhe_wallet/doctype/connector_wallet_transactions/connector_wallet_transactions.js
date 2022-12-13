// Copyright (c) 2022, Administrator and contributors
// For license information, please see license.txt

frappe.ui.form.on('Connector Wallet Transactions', {
	refresh: function(frm) {
		frm.add_custom_button(__("Sync Transaction"), function(){
			if(frm.doc.is_sync == 1){
        	                frappe.throw("Transaction already synced")
	                }

			frappe.call({
				'method': 'maqadhe_wallet.api.create_jv_for_transactions',
				'freeze':true,
				'args':{
				   'tsn_id':frm.doc.name
				},
				'callback':function(res){
					if(res.message){
					}
				}


			})
		});

	}
});
