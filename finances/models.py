from django.db import models
from users.models import User

class Person(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="persons")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60, blank=True, null=True)
    relation = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}"

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=60)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    is_income = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    monthly_budget = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.monthly_budget}"


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallets")
    name = models.CharField(max_length=60)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    date = models.DateTimeField()
    text = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.text} - {self.amount}"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    date = models.DateTimeField()
    text = models.CharField(max_length=30)
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)

    def __str__(self):
        return f"{self.text} - {self.amount}"

class Debt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    text = models.CharField(max_length=30)
    date = models.DateTimeField()
    pay_date = models.DateTimeField()

    def __str__(self):
        return f"Debt: {self.amount}"

class Credit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    text = models.CharField(max_length=30)
    date = models.DateTimeField()
    pay_date = models.DateTimeField()

    def __str__(self):
        return f"Credit: {self.amount}"

class Installment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    text = models.CharField(max_length=30)
    first_date = models.DateTimeField()
    pay_period = models.IntegerField()  # 1=monthly, 2=bimonthly
    inst_num = models.IntegerField()
    inst_rate = models.IntegerField(null=True, blank=True)  # interest rate

    def __str__(self):
        return self.text

class InstallmentDetail(models.Model):
    installment = models.ForeignKey(Installment, on_delete=models.CASCADE, related_name="details")
    inst_num = models.IntegerField()
    payment_status = models.CharField(max_length=20, choices=[("paid", "Paid"), ("unpaid", "Unpaid")])
    payment_date = models.DateTimeField()
    amount = models.IntegerField()

    def __str__(self):
        return f"Installment {self.inst_num} - {self.payment_status}"
