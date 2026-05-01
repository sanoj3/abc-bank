from django.db import models, transaction as db_transaction
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    aadhar_number = models.CharField(max_length=12, unique=True)
    phone_number = models.CharField(max_length=15)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    account_number = models.CharField(max_length=20, unique=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            with db_transaction.atomic():
                last_customer = Customer.objects.select_for_update().order_by('-id').first()

                if last_customer and last_customer.account_number:
                    new_number = int(last_customer.account_number)+1
                else:
                    new_number = 525053000000000
                self.account_number = new_number
        super().save(*args, **kwargs)
    def __str__(self):
        return self.user.username
    

class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw')
    )
    customer = models.ForeignKey(Customer, on_delete= models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    after_balance = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    

    def __str__(self):
        return f"{self.customer.user.username} - {self.transaction_type} - {self.amount}"