def topup_failed (self, body, data, transaction):
    print('******FAILURE********', body)
    source_currency = 'KES'
    transaction.state = self.model.ProcessingState.FAILED.label
    transaction.transaction_id = data.get('CheckoutRequestID')
    transaction.source_currency = source_currency
    transaction.description = data.get('ResultDesc')
    transaction.serial = data.get('MerchantRequestID')
    transaction.save()
    return body
