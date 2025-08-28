from django.contrib import admin
from .models import Fund, FundMembership, Contribution, Payout

admin.site.register(Fund)
admin.site.register(FundMembership)
admin.site.register(Contribution)
admin.site.register(Payout)
