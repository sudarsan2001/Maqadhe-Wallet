# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "maqadhe_wallet"
app_title = "Maqadhe Wallet"
app_publisher = "Administrator"
app_description = "Wallet Transactions"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "admin@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/maqadhe_wallet/css/maqadhe_wallet.css"
# app_include_js = "/assets/maqadhe_wallet/js/maqadhe_wallet.js"

# include js, css files in header of web template
# web_include_css = "/assets/maqadhe_wallet/css/maqadhe_wallet.css"
# web_include_js = "/assets/maqadhe_wallet/js/maqadhe_wallet.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "maqadhe_wallet.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "maqadhe_wallet.install.before_install"
# after_install = "maqadhe_wallet.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "maqadhe_wallet.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"maqadhe_wallet.tasks.all"
# 	],
# 	"daily": [
# 		"maqadhe_wallet.tasks.daily"
# 	],
# 	"hourly": [
# 		"maqadhe_wallet.tasks.hourly"
# 	],
# 	"weekly": [
# 		"maqadhe_wallet.tasks.weekly"
# 	]
# 	"monthly": [
# 		"maqadhe_wallet.tasks.monthly"
# 	]
# }

scheduler_events = {
        "cron": {
                "*/30 * * * *":[
                        "maqadhe_wallet.api.create_wallet_balance"
                ],
                "0 3 * * *":[
                        "maqadhe_wallet.api.get_wallet_transactions"
                ],
                "*/5 * * * *": [
                        "maqadhe_wallet.api.create_jv_for_transactions"
                ]
        }
}

# Testing
# -------

# before_tests = "maqadhe_wallet.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "maqadhe_wallet.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "maqadhe_wallet.task.get_dashboard_data"
# }

