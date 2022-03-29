BAD_REQUEST = "Bad request"
INTERNAL_SERVER_ERROR = "Oupss, something went wrong"
CONFLICT = "{}already exists"
NOT_FOUND = "{}not found"
REQUIRED = "{}required"
WRONG_PHONE_NUMBER = "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
WRONG_EMAIL = "wrong email address"

# auth
WRONG_TOKEN = "wrong token"
WRONG_OTP = "wrong verification code"
TOKEN_EXPIRED = "your token has expired"
MALFORMED_PAYLOAD = "Could not validate credentials"
AUTHENTICATION_REQUIRED = "authentication required"
ACCESS_DENIED = "access denied! Not enough permissions"
EMAIL_NOT_VERIFIED = "email not verified"
PHONE_NOT_VERIFIED = "phone number not verified"
WRONG_CREDENTAILS = "wrong email or PIN"
WRONG_PIN = "wrong PIN"
ACCOUNT_LOCKED_DUE_WRONG_LOGIN_ATTEMPTS = "your account is locked due to multiple unsuccessful login attempts. It will be unlocked automatically in 24 hours"
ACCOUNT_LOCKED_DUE_TO_SUSPICIOUS_ACTIVITIES = "your account is locked due to suspicious activities"

# user
PHONE_NUMBER_TAKEN = "user with this phone number{} already exists"
PHONE_NUMBER_EXIST = "this phone number{} already exists"
EMAIL_TAKEN = "user with this email{} already exists"

# transactions
INVALID_AMOUNT = "amount can not be a negative number or 0"
INSUFFICIENT_FUNDS = "You do not have enough funds. Please top-up your wallet to perform this transaction"
SAME_SOURCE_TARGET_WALLET = "The source and target wallet can not be the same"

# fees
INVALID_FEE_TYPE = "fee type is invalid, types allowed are flat or percentage"

# m-pesa
M_PESA_TOKEN_EXPIRED='404.001.03'
