import re
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from apps.companies.models import Company


class Category(models.Model):
    """Category model for transaction categorization"""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="categories"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#9E9E9E")  # Hex color
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        db_table = "categories"
        unique_together = [["company", "name"]]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate category constraints"""
        super().clean()
        
        # Prevent self-reference
        if self.parent == self:
            raise ValidationError("A category cannot be its own parent.")
        
        # Prevent circular references
        if self.parent and self._would_create_cycle():
            raise ValidationError("This would create a circular reference.")

    def _would_create_cycle(self):
        """Check if setting this parent would create a circular reference"""
        current = self.parent
        while current:
            if current == self:
                return True
            current = current.parent
        return False

    def get_children(self):
        """Get direct children of this category"""
        return Category.objects.filter(parent=self, is_active=True)

    def get_descendants(self):
        """Get all descendants of this category"""
        descendants = Category.objects.filter(parent=self)
        for child in descendants:
            descendants = descendants | child.get_descendants()
        return descendants

    def get_ancestors(self):
        """Get all ancestors of this category"""
        ancestors = Category.objects.none()
        current = self.parent
        while current:
            ancestors = ancestors | Category.objects.filter(id=current.id)
            current = current.parent
        return ancestors

    def get_full_path(self):
        """Get full hierarchical path of this category"""
        path_parts = [self.name]
        current = self.parent
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        return " > ".join(path_parts)


class CategorizationRule(models.Model):
    """Rule for automatic transaction categorization"""

    CONDITION_TYPE_CHOICES = [
        ("CONTAINS", "Contains"),
        ("EQUALS", "Equals"),
        ("STARTS_WITH", "Starts with"),
        ("ENDS_WITH", "Ends with"),
        ("REGEX", "Regular expression"),
        ("GREATER_THAN", "Greater than"),
        ("LESS_THAN", "Less than"),
        ("GREATER_EQUAL", "Greater than or equal"),
        ("LESS_EQUAL", "Less than or equal"),
    ]

    FIELD_NAME_CHOICES = [
        ("description", "Description"),
        ("amount", "Amount"),
        ("transaction_type", "Transaction Type"),
        ("category", "Category"),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="categorization_rules"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="rules"
    )
    name = models.CharField(max_length=100)
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPE_CHOICES)
    field_name = models.CharField(max_length=50, choices=FIELD_NAME_CHOICES)
    field_value = models.CharField(max_length=500)
    priority = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "name"]
        db_table = "categorization_rules"
        unique_together = [["company", "name"]]

    def __str__(self):
        return self.name

    def matches_transaction(self, transaction_data):
        """Check if this rule matches the given transaction data"""
        field_value = transaction_data.get(self.field_name)
        if field_value is None:
            return False

        # Convert to string for text operations
        field_value_str = str(field_value).lower()
        rule_value_str = self.field_value.lower()

        try:
            if self.condition_type == "CONTAINS":
                return rule_value_str in field_value_str
            
            elif self.condition_type == "EQUALS":
                return field_value_str == rule_value_str
            
            elif self.condition_type == "STARTS_WITH":
                return field_value_str.startswith(rule_value_str)
            
            elif self.condition_type == "ENDS_WITH":
                return field_value_str.endswith(rule_value_str)
            
            elif self.condition_type == "REGEX":
                return bool(re.search(self.field_value, field_value_str, re.IGNORECASE))
            
            elif self.condition_type in ["GREATER_THAN", "LESS_THAN", "GREATER_EQUAL", "LESS_EQUAL"]:
                # Numeric comparisons
                try:
                    field_numeric = Decimal(str(field_value))
                    rule_numeric = Decimal(self.field_value)
                    
                    if self.condition_type == "GREATER_THAN":
                        return field_numeric > rule_numeric
                    elif self.condition_type == "LESS_THAN":
                        return field_numeric < rule_numeric
                    elif self.condition_type == "GREATER_EQUAL":
                        return field_numeric >= rule_numeric
                    elif self.condition_type == "LESS_EQUAL":
                        return field_numeric <= rule_numeric
                        
                except (ValueError, TypeError, Decimal.InvalidOperation):
                    return False
            
            return False
            
        except (re.error, ValueError, TypeError):
            # Handle regex errors or other exceptions
            return False
