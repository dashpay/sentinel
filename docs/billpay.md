
help:

	Use one of these commands:

	user [create|modify|]
	invoice [create|modify|send] username amount
	billpay [create|modify] username amount_owed_max


>> create sara, with password Httr...

To create the relationship, first you must create the billpay:

>> Sara types: "billpay [create|modify] perry 500"

Then Node40 will type the following to receive automatic payment

>> perry types "invoice create eduffield 455.234"
>> perry types "invoice send eduffield 455.234"

