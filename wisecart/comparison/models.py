from django.db import models
from django.contrib.sessions.models import Session
from products.models import Product


class ComparisonSession(models.Model):
    """Model to track comparison sessions using Django sessions"""
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comparison_session'
        
    def __str__(self):
        return f"Comparison Session {self.session_key}"


class ComparedProduct(models.Model):
    """Model to store products added to comparison"""
    comparison_session = models.ForeignKey(ComparisonSession, on_delete=models.CASCADE, related_name='compared_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'compared_product'
        unique_together = ('comparison_session', 'product')
        
    def __str__(self):
        return f"{self.product.name} in {self.comparison_session.session_key}"
