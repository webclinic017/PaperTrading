from django import forms


class SearchForm(forms.Form):
    company = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Company name or ticker...'}))


class PlaceOrder(forms.Form):

    type_values = (('Market', 'Market'), ('Limit', 'Limit'), ('Stop', 'Stop'), ('StopLimit', 'Stop Limit'))
    timeForce_values = (('Day', 'Day'), ('Gtc', 'Gtc'), ('Opg', 'Opg'))

    quantity = forms.IntegerField(label='Quantity', help_text='Amount of shares to purchase', min_value=1)
    type = forms.ChoiceField(widget=forms.Select, choices=type_values)
    time_force = forms.ChoiceField(widget=forms.Select, choices=timeForce_values)
    limit_price = forms.IntegerField(label='Limit Price', help_text='This is limit price', required=False)
    stop_price = forms.IntegerField(label='Stop Price', help_text='this is stop price', required=False)

    class Meta:
        fields = ['type', 'timeForce', 'limitPrice', 'stopPrice']

    def clean_limit_price(self, *args, **kwargs):
        clean_type = self.cleaned_data.get("type")
        limit_price = self.cleaned_data.get("limit_price")

        if "Market" == clean_type or "Stop" == clean_type:
            limit_price = 0
            return limit_price

        if "Limit" == clean_type or "Limit Stop" == clean_type:
            if limit_price is None:
                raise forms.ValidationError("Limit price is can not be less that 1")
            elif limit_price < 1:
                raise forms.ValidationError("Limit price is can not be less that 1")

        return limit_price

    def clean_stop_price(self, *args, **kwargs):
        clean_type = self.cleaned_data.get("type")
        stop_price = self.cleaned_data.get("stop_price")

        if "Market" == clean_type or "Limit" == clean_type:
            stop_price = 0
            return stop_price

        if "Stop" == clean_type or "Limit Stop" == clean_type:
            if stop_price is None:
                raise forms.ValidationError("Limit price is can not be less that 1")
            elif stop_price < 1:
                raise forms.ValidationError("Limit price is can not be less that 1")

        return stop_price


    # def clean_renewal_date(self):
    #     data = self.cleaned_data['renewal_date']
    #
    #     # Check if a date is not in the past.
    #     if data < datetime.date.today():
    #         raise ValidationError(_('Invalid date - renewal in past'))
    #
    #     # Check if a date is in the allowed range (+4 weeks from today).
    #     if data > datetime.date.today() + datetime.timedelta(weeks=4):
    #         raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
    #
    #     # Remember to always return the cleaned data.
    #     return data

