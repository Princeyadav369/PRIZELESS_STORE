from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image', 'colors', 'display_section', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded p-2.5 bg-gray-50 text-gray-900'}),
            'category': forms.Select(attrs={'class': 'w-full border rounded p-2.5 bg-gray-50 text-gray-900'}),
            'price': forms.NumberInput(attrs={'class': 'w-full border rounded p-2.5 bg-gray-50 text-gray-900'}),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded p-2.5 bg-gray-50 text-gray-900', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full border rounded p-2.5 bg-gray-50 text-gray-900'}),
            'colors': forms.TextInput(attrs={'class': 'w-full border rounded p-2.5 bg-gray-50 text-gray-900', 'placeholder': 'e.g. Red, Blue, Black (Optional)'}),
            'display_section': forms.Select(attrs={'class': 'w-full border rounded p-2.5 bg-gray-50 text-gray-900'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-orange-600'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded p-2.5 bg-gray-50 text-gray-900'}),
        }