"""
	genius-cli [command] 

	Help:

	balance
	private_balance
	sendto
	listtransactions

	# setup a user, group, company and a contract

	user create "evan", "evan@gmail.com", "your-new-password"
	user update "eduffield" "email" "evan@dash.org" #correct invalid amount
	user show "eduffield"
	{
		Name: Evan Duffield
		Average Rating: 3.14
		URL: https://foundation.dash.org/us/employees/eduffield
		Contracts: ["empl-eduffield-2016"]
	}

	user find "eduff*"
	{
		Name: Evan Duffield
		Level: XIII
		Average Rating: 3.14
		URL: https://foundation.dash.org/us/employees/eduffield
		Contracts: ["empl-eduffield-2016"]
	}

	proposal "dashtalk-acquire-v2", "https://www.dashwhale.org/p/dashtalk-acquire-v2", start-time, end-time, user-h256
	proposal show "dashtalk-acquire-v2"
	{
		Name: "dashtalk-acquire-v2",
		Yes: 37%
		No: 55%
	}
	proposal vote "dashtalk-acquire-v2" "funding" No

	governance amend "Article 1.1" "The network shall have a secure, limited supply whereby the emissions never exceeds 19 million units"
	governance vote "Article 1.1" yes
	governance list
	{
		"Article 1.1" : "The network shall have a secure, limited supply whereby the emissions never exceeds 19 million units",
	}

	group create "testgroup"
	group add "testgroup", "eduffield"

	company create "core", "password"
		{
			Name: "core"
			Groups: ["core-employees"]
		}

	group add "core-employees" 'eduffield'
	group delete "testgroup"

	company show "core"
	{
		Name: "core",
		Groups: ["core-employees"],
		Employees: ["eduffield"]
	}

	contract create "eduffield-2016", "https://www.dash.org/contracts/eduffield-2016", 2016/1/1, 2016-12-31, 3200 DASH
	contract show "eduffield-2016"
	{
		Name: "Evan Duffield",
		Yes: 99%
		No: 0%
	}
	contract vote eduffield-2016 funding yes
	contract show "eduffield-2016"
	{
		Name: "Evan Duffield",
		Yes: 100%
	}

	company show "core"
	{
		Name: "core",
		Groups: ["core-employees"],
		Employees: ["eduffield (active contract)"]
	}

	contract update "eduffield-2016" "amount" "3300 DASH"

"""