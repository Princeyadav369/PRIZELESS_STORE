from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded p-2.5'}),
            'category': forms.Select(attrs={'class': 'w-full border rounded p-2.5'}),
            'price': forms.NumberInput(attrs={'class': 'w-full border rounded p-2.5'}),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded p-2.5', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full border rounded p-2.5'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-orange-600'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded p-2.5'}),
        }