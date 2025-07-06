import re
from rest_framework import serializers
from .models import Category, CategorizationRule


class CategoryParentSerializer(serializers.ModelSerializer):
    """Simplified serializer for parent category in nested representation"""

    class Meta:
        model = Category
        fields = ["id", "name", "color"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model with nested parent"""

    parent = CategoryParentSerializer(read_only=True)
    full_path = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    rules_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "company",
            "parent",
            "name",
            "color",
            "is_system",
            "is_active",
            "full_path",
            "children_count",
            "rules_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "full_path", "children_count", "rules_count"]

    def get_full_path(self, obj):
        """Get the full hierarchical path of the category"""
        return obj.get_full_path()

    def get_children_count(self, obj):
        """Get the number of direct children"""
        return obj.get_children().count()

    def get_rules_count(self, obj):
        """Get the number of categorization rules for this category"""
        return obj.rules.filter(is_active=True).count()


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Category"""

    class Meta:
        model = Category
        fields = [
            "company",
            "parent",
            "name",
            "color",
            "is_system",
            "is_active",
        ]

    def validate_color(self, value):
        """Validate that color is a valid hex color"""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError("Color must be a valid hex color (e.g., #FF0000)")
        return value

    def validate(self, data):
        """Validate category constraints"""
        # Check for duplicate name in same company
        company = data.get('company')
        name = data.get('name')
        
        if company and name:
            if Category.objects.filter(company=company, name=name).exists():
                raise serializers.ValidationError({
                    'name': 'A category with this name already exists in this company.'
                })
        
        return data


class CategoryNestedSerializer(serializers.ModelSerializer):
    """Simplified category serializer for use in other models"""

    class Meta:
        model = Category
        fields = ["id", "name", "color", "full_path"]

    full_path = serializers.SerializerMethodField()

    def get_full_path(self, obj):
        return obj.get_full_path()


class CategorizationRuleSerializer(serializers.ModelSerializer):
    """Serializer for CategorizationRule model with nested category"""

    category = CategoryNestedSerializer(read_only=True)
    condition_display = serializers.SerializerMethodField()
    field_display = serializers.SerializerMethodField()

    class Meta:
        model = CategorizationRule
        fields = [
            "id",
            "company",
            "category",
            "name",
            "condition_type",
            "condition_display",
            "field_name",
            "field_display",
            "field_value",
            "priority",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "condition_display", "field_display"]

    def get_condition_display(self, obj):
        """Get human-readable condition type"""
        return obj.get_condition_type_display()

    def get_field_display(self, obj):
        """Get human-readable field name"""
        return obj.get_field_name_display()


class CategorizationRuleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating CategorizationRule"""

    class Meta:
        model = CategorizationRule
        fields = [
            "company",
            "category",
            "name",
            "condition_type",
            "field_name",
            "field_value",
            "priority",
            "is_active",
        ]

    def validate_field_value(self, value):
        """Validate field value based on condition type and field name"""
        condition_type = self.initial_data.get('condition_type')
        field_name = self.initial_data.get('field_name')

        # Validate regex patterns
        if condition_type == 'REGEX':
            try:
                re.compile(value)
            except re.error:
                raise serializers.ValidationError("Invalid regular expression pattern.")

        # Validate numeric values for amount-based conditions
        if field_name == 'amount' and condition_type in ['GREATER_THAN', 'LESS_THAN', 'GREATER_EQUAL', 'LESS_EQUAL']:
            try:
                float(value)
            except ValueError:
                raise serializers.ValidationError("Field value must be a valid number for amount-based conditions.")

        return value

    def validate(self, data):
        """Validate rule constraints"""
        # Check for duplicate name in same company
        company = data.get('company')
        name = data.get('name')
        
        if company and name:
            if CategorizationRule.objects.filter(company=company, name=name).exists():
                raise serializers.ValidationError({
                    'name': 'A rule with this name already exists in this company.'
                })
        
        return data