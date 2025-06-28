from django import forms
from .models import Customer, Product, Expense,Lens


# 1. Sales Report Form (كان موجوداً)
class SalesReportForm(forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), required=False, label='العميل')
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, label='المنتج')
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='من تاريخ')
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='إلى تاريخ')

# 2. Expense Form (كان موجوداً)
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'notes']
        labels = {
            'title': 'اسم المصروف',
            'amount': 'المبلغ',
            'category': 'الفئة',
            'notes': 'ملاحظات',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'border-2 border-gray-600 rounded-lg p-2 w-full',
                'placeholder': 'أدخل اسم المصروف'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'border-2 border-gray-600 rounded-lg p-2 w-full',
                'placeholder': 'أدخل المبلغ'
            }),
            'category': forms.Select(attrs={
                'class': 'border-2 border-gray-600 rounded-lg p-2 w-full',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'border-2 border-gray-600 rounded-lg p-2 w-full',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
        }

# 3. Product Form (تم إضافته)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'buy_price', 'sell_price', 'quantity', 'barcode']
        labels = {
            'name': 'اسم المنتج',
            'category': 'الفئة',
            'brand': 'العلامة التجارية',
            'buy_price': 'سعر الشراء',
            'sell_price': 'سعر البيع',
            'quantity': 'الكمية',
            'barcode': 'الباركود',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'أدخل اسم المنتج'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
            }),
            'brand': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'أدخل العلامة التجارية (اختياري)'
            }),
            'buy_price': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01', # مهم للأرقام العشرية
                'placeholder': 'سعر الشراء'
            }),
            'sell_price': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01', # مهم للأرقام العشرية
                'placeholder': 'سعر البيع'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'الكمية المتاحة'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'أدخل الباركود (اختياري)'
            }),
        }
    # إضافة validation مخصص للأسعار والكمية
    def clean(self):
        cleaned_data = super().clean()
        buy_price = cleaned_data.get('buy_price')
        sell_price = cleaned_data.get('sell_price')
        quantity = cleaned_data.get('quantity')

        if buy_price is not None and buy_price < 0:
            self.add_error('buy_price', 'سعر الشراء لا يمكن أن يكون سالباً.')
        
        if sell_price is not None and sell_price < 0:
            self.add_error('sell_price', 'سعر البيع لا يمكن أن يكون سالباً.')

        if sell_price is not None and buy_price is not None and sell_price < buy_price:
            self.add_error('sell_price', 'سعر البيع لا يمكن أن يكون أقل من سعر الشراء.')

        if quantity is not None and quantity < 0:
            self.add_error('quantity', 'الكمية في المخزن لا يمكن أن تكون سالبة.')

        return cleaned_data

# 4. Customer Form (تم إضافته)
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address', 'notes']
        labels = {
            'name': 'اسم العميل',
            'phone': 'رقم الهاتف',
            'address': 'العنوان',
            'notes': 'ملاحظات',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'اسم العميل'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full p-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'رقم الهاتف'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full p-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'عنوان العميل'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full p-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("اسم العميل مطلوب.")
        return name

# 5. Lens Form (تم إضافته)
class LensForm(forms.ModelForm):
    class Meta:
        model = Lens
        fields = ['name', 'company', 'buy_price', 'sell_price']
        labels = {
            'name': 'اسم العدسة',
            'company': 'اسم الشركة (اختياري)',
            'buy_price': 'سعر الشراء',
            'sell_price': 'سعر البيع',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'اسم العدسة'
            }),
            'company': forms.TextInput(attrs={
                'class': 'w-full p-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'اسم الشركة (اختياري)'
            }),
            'buy_price': forms.NumberInput(attrs={
                'class': 'w-full p-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'سعر الشراء'
            }),
            'sell_price': forms.NumberInput(attrs={
                'class': 'w-full p-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'سعر البيع'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("اسم العدسة مطلوب.")
        return name